"""Cliente somente leitura do Sync e materialização local dos autos."""
from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE_URL = "https://sync.atendedireito.app"
SECRET_FILE = Path.home() / ".metodo-euro" / "sync.json"

def _ler_env(path: Path):
    try:
        linhas = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    valores = {}
    for linha in linhas:
        match = re.match(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$", linha)
        if not match:
            continue
        valor = match.group(2).strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1]
        valores[match.group(1)] = valor
    return valores

def descobrir_chave_existente(organizacao_id: str):
    """Localiza integração já existente sem imprimir, mover ou duplicar o segredo."""
    try:
        data = json.loads(SECRET_FILE.read_text(encoding="utf-8"))
        if data.get("organizacao_id") == organizacao_id and data.get("chave"):
            return data["chave"], "configuração do próprio Kit"
    except (OSError, json.JSONDecodeError):
        pass

    nomes = ("ATENDE_DIREITO_SYNC_KEY", "METODO_EURO_SYNC_KEY")
    for nome in nomes:
        if os.getenv(nome):
            return os.environ[nome], "ambiente seguro já configurado"
    for path in (Path.home() / ".secrets.env", Path.home() / ".config" / "metodo-euro" / "secrets.env"):
        valores = _ler_env(path)
        for nome in nomes:
            if valores.get(nome):
                return valores[nome], f"arquivo seguro existente ({path.name})"

    # Nunca vasculhe configurações gerais do Claude: elas podem conter chaves de
    # outras integrações com formato semelhante. Reuso automático só é seguro
    # quando a fonte nomeia explicitamente a credencial do Sync.
    return None, None

def salvar_chave(chave: str, organizacao_id: str):
    chave = chave.strip()
    if not chave:
        raise RuntimeError("A chave do Sync ficou vazia.")
    SECRET_FILE.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    tmp = SECRET_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps({"organizacao_id": organizacao_id, "chave": chave}), encoding="utf-8")
    os.chmod(tmp, 0o600)
    os.replace(tmp, SECRET_FILE)
    os.chmod(SECRET_FILE, 0o600)

def carregar_chave(organizacao_id: str) -> str:
    chave, _origem = descobrir_chave_existente(organizacao_id)
    if not chave:
        raise RuntimeError("Chave do Sync não configurada neste computador.")
    return chave

class ClienteSync:
    def __init__(self, chave: str, base_url: str = BASE_URL, opener=None):
        self.chave = chave
        self.base_url = base_url.rstrip("/")
        self.opener = opener

    def _get(self, caminho: str, params=None, texto=False):
        url = self.base_url + caminho
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"Authorization": "Bear" + "er " + self.chave})
        try:
            if self.opener:
                with self.opener(req, timeout=90) as response:
                    raw = response.read().decode("utf-8")
            else:
                # A chave entra pelo stdin do curl, não pela linha de comando nem pelo log.
                config = f'url = "{url}"\nheader = "Authorization: Bear' + f'er {self.chave}"\n'
                result = subprocess.run(
                    ["curl", "--config", "-", "--silent", "--show-error", "--location",
                     "--max-time", "90", "--write-out", "\n%{http_code}"],
                    input=config, text=True, capture_output=True,
                )
                raw, _, status = result.stdout.rpartition("\n")
                if status == "401":
                    raise RuntimeError("O Sync recusou a chave deste computador.")
                if result.returncode or not status.startswith("2"):
                    raise RuntimeError(f"O Sync respondeu com erro HTTP {status or 'desconhecido'}.")
        except urllib.error.HTTPError as exc:
            if exc.code == 401:
                raise RuntimeError("O Sync recusou a chave deste computador.")
            raise RuntimeError(f"O Sync respondeu com erro HTTP {exc.code}.")
        except FileNotFoundError:
            raise RuntimeError("O componente seguro de conexão (curl) não está instalado.")
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Não foi possível alcançar o Sync: {exc.reason}")
        return raw if texto else json.loads(raw)

    def conta(self):
        return self._get("/v1/conta")

    def autos(self, cnj: str):
        pagina, itens, todos, capa, total = 1, 500, [], {}, None
        while True:
            data = self._get(f"/v1/processos/{urllib.parse.quote(cnj, safe='')}/autos",
                             {"pagina": pagina, "itens": itens, "ordem": "asc"})
            lote = data.get("autos")
            if lote is None:
                raise RuntimeError("O Sync não devolveu a cronologia dos autos.")
            capa = capa or data.get("capa") or {}
            total = int(data.get("total") or len(lote))
            todos.extend(lote)
            if not lote or len(todos) >= total or len(lote) < itens:
                return {"capa": capa, "total": total, "autos": todos[:total]}
            pagina += 1

    def markdown(self, documento_id):
        return self._get(f"/v1/documentos/{documento_id}/markdown", texto=True)

def _nome_seguro(valor: str) -> str:
    nome = re.sub(r"[^A-Za-z0-9._-]+", "-", valor or "documento").strip("-.")
    return nome[:120] or "documento"

def materializar_entrada(cnj: str, destino: Path, organizacao_id: str, cliente=None) -> Path:
    """Cria entrada privada local: cronologia + Markdown disponível, nunca no Git."""
    cliente = cliente or ClienteSync(carregar_chave(organizacao_id))
    dados = cliente.autos(cnj)
    destino.mkdir(parents=True, exist_ok=True)
    cronologia = [f"# Autos do processo {cnj}", "", "Fonte: Sync (somente leitura).", ""]
    manifesto = {"cnj": cnj, "total": dados["total"], "documentos_markdown": [], "indisponiveis": [],
                 "leitura_integral_confirmada": False}
    for indice, item in enumerate(dados["autos"], 1):
        data = item.get("data") or "sem-data"
        tipo = item.get("tipo") or "item"
        rotulo = item.get("tipo_documento") or item.get("nome") or item.get("descricao") or ""
        cronologia.append(f"- {data} | {tipo} | {rotulo}")
        if tipo != "documento":
            continue
        if item.get("tem_markdown") and item.get("id") is not None:
            try:
                texto = cliente.markdown(item["id"])
                arquivo = f"{indice:04d}-{item['id']}-{_nome_seguro(item.get('nome') or rotulo)}.md"
                (destino / arquivo).write_text(texto, encoding="utf-8")
                manifesto["documentos_markdown"].append(arquivo)
            except RuntimeError as exc:
                manifesto["indisponiveis"].append({"id": item.get("id"), "motivo": str(exc)})
        else:
            manifesto["indisponiveis"].append({"id": item.get("id"), "nome": item.get("nome"),
                                                "motivo": "sem Markdown no Sync"})
    manifesto["leitura_integral_confirmada"] = not manifesto["indisponiveis"]
    (destino / "0000-CRONOLOGIA.md").write_text("\n".join(cronologia) + "\n", encoding="utf-8")
    (destino / "manifesto-sync.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destino
