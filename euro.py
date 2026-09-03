#!/usr/bin/env python3
"""CLI sem dependências do Kit 2 Método Euro."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import platform
import uuid
import getpass
from datetime import datetime, timezone
from pathlib import Path

from conectores import sync as sync_connector

ROOT = Path(__file__).resolve().parent
LOCAL = ROOT / ".metodo-euro.local.json"
SHARED = ROOT / "metodo-euro.json"
VALID_ROLES = {"dono", "controller", "advogado"}
VALID_AGENTS = {"claude", "codex"}
TRANSITIONS = {
    "aberta": {"em_execucao"},
    "em_execucao": {"entregue"},
    "entregue": {"aprovada", "ajustes", "reprovada"},
    "ajustes": {"em_execucao"},
}

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def load(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)

def repo_url():
    result = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else ""

def make_invite(shared, papel="advogado"):
    if papel not in {"controller", "advogado"}:
        raise SystemExit("Código de entrada permitido somente para Controller ou Advogado.")
    org = shared.get("organizacao") or {}
    payload = {"v": 1, "organizacao_id": org.get("id"), "escritorio": shared.get("nome_escritorio"),
               "repositorio": org.get("repositorio"), "papel": papel}
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(raw).decode().rstrip("=")
    return f"EURO1.{body}.{hashlib.sha256(raw).hexdigest()[:12]}"

def read_invite(code):
    try:
        prefix, body, check = code.strip().split(".", 2)
        if prefix != "EURO1": raise ValueError
        raw = base64.urlsafe_b64decode(body + "=" * (-len(body) % 4))
        if hashlib.sha256(raw).hexdigest()[:12] != check: raise ValueError
        data = json.loads(raw)
        if not all(data.get(k) for k in ("organizacao_id", "escritorio", "repositorio")): raise ValueError
        return data
    except (ValueError, json.JSONDecodeError):
        raise SystemExit("Código de entrada inválido ou alterado. Solicite outro ao Controller.")

def auto_git(paths, message):
    if os.getenv("METODO_EURO_NO_AUTO_GIT") == "1" or not (ROOT / ".git").exists(): return
    local = load(LOCAL) if LOCAL.exists() else {}
    if not local.get("sincronizacao_automatica", True): return
    subprocess.run(["git", "add", "--", *paths], cwd=ROOT, check=True, capture_output=True)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode:
        subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True, capture_output=True)
    pull = subprocess.run(["git", "pull", "--rebase"], cwd=ROOT, capture_output=True, text=True)
    if pull.returncode:
        subprocess.run(["git", "rebase", "--abort"], cwd=ROOT, capture_output=True)
        raise SystemExit("Sincronização encontrou conflito. As duas versões foram preservadas para conciliação.")
    if subprocess.run(["git", "push"], cwd=ROOT, capture_output=True).returncode:
        raise SystemExit("A alteração ficou salva neste computador, mas o envio automático ao escritório falhou.")

def pull_before_read():
    if os.getenv("METODO_EURO_NO_AUTO_GIT") == "1" or not (ROOT / ".git").exists(): return
    if subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True).stdout: return
    subprocess.run(["git", "pull", "--rebase"], cwd=ROOT, capture_output=True)

def config():
    if not LOCAL.exists():
        raise SystemExit("Configuração local ausente. Execute: python3 euro.py configurar")
    return load(LOCAL), load(SHARED)

def local_roles(local):
    return set(local.get("papeis") or [local.get("papel")])

def require_role(expected):
    local, shared = config()
    if expected not in local_roles(local):
        raise SystemExit(f"Ação exclusiva de {expected}; papel local: {', '.join(sorted(local_roles(local)))}")
    return local, shared

def task_path(task_id):
    path = ROOT / "fila" / f"{task_id}.json"
    if not path.exists():
        raise SystemExit(f"Tarefa não encontrada: {task_id}")
    return path

def task(task_id):
    return load(task_path(task_id))

def event(data, action, actor, detail=""):
    data.setdefault("historico", []).append({"em": now(), "acao": action, "por": actor, "detalhe": detail})

def transition(data, target):
    current = data["status"]
    if target not in TRANSITIONS.get(current, set()):
        raise SystemExit(f"Transição inválida: {current} → {target}")
    data["status"] = target

def cmd_configure(a):
    if a.papel not in VALID_ROLES or a.agente not in VALID_AGENTS:
        raise SystemExit("Papel ou agente inválido.")
    shared = load(SHARED)
    org = shared.get("organizacao") or {}
    if a.papel == "controller" and org.get("controllers") and a.nome not in org["controllers"]:
        raise SystemExit("Somente o Dono pode nomear Controllers por código de entrada.")
    data = {"schema_version": 1, "colaborador": a.nome, "papel": a.papel, "papeis": [a.papel],
            "agente": a.agente, "repositorio_privado_confirmado": a.repositorio_privado_confirmado,
            "sincronizacao_automatica": True, "organizacao_id": org.get("id"),
            "configurado_em": now()}
    save(LOCAL, data)
    if shared["nome_escritorio"] == "CONFIGURE-ME" and a.escritorio:
        shared["nome_escritorio"] = a.escritorio
        save(SHARED, shared)
    print("OK — configuração local salva fora do Git; modo compartilhado:", shared["modo"])

def cmd_start_office(a):
    shared = load(SHARED)
    org = shared.get("organizacao") or {}
    if org.get("id") and org.get("dono") != a.nome:
        raise SystemExit("Este escritório já tem um Dono/Administrador registrado.")
    if not org.get("id"):
        shared["nome_escritorio"] = a.escritorio
        shared["organizacao"] = {"id": str(uuid.uuid4()), "dono": a.nome,
                                 "controllers": [a.nome] if a.tambem_controller else [],
                                 "repositorio": a.repositorio or repo_url(), "criada_em": now()}
        if not shared["organizacao"]["repositorio"]: raise SystemExit("Repositório privado não identificado.")
        save(SHARED, shared)
    previous = load(LOCAL) if LOCAL.exists() else {}
    papeis = ["dono"] + (["controller"] if a.tambem_controller else [])
    local = {"schema_version": 1, "colaborador": a.nome, "papel": "dono", "papeis": papeis, "agente": a.agente,
             "repositorio_privado_confirmado": True, "sincronizacao_automatica": True,
             "organizacao_id": shared["organizacao"]["id"],
             "raizes_entrada": previous.get("raizes_entrada", {}), "configurado_em": now()}
    save(LOCAL, local)
    auto_git([str(SHARED.relative_to(ROOT))], "config: iniciar escritório e congelar Dono")
    print("OK — escritório criado. Dono/Administrador:", a.nome)
    print("PAPÉIS LOCAIS:", ", ".join(papeis))

def cmd_join(a):
    invite = read_invite(a.codigo)
    shared = load(SHARED); org = shared.get("organizacao") or {}
    if invite["organizacao_id"] != org.get("id") or invite["escritorio"] != shared.get("nome_escritorio"):
        raise SystemExit("O código pertence a outro escritório ou a outra cópia do Kit.")
    papel = invite.get("papel")
    if papel not in {"controller", "advogado"}:
        raise SystemExit("O código não contém um papel permitido.")
    local = {"schema_version": 1, "colaborador": a.nome, "papel": papel, "papeis": [papel], "agente": a.agente,
             "repositorio_privado_confirmado": True, "sincronizacao_automatica": True,
             "organizacao_id": org["id"], "raizes_entrada": {}, "configurado_em": now()}
    save(LOCAL, local)
    print("OK — entrada concluída no escritório:", shared["nome_escritorio"])
    print("Papel:", papel.title(), "| Dono/Administrador:", org.get("dono"))

def cmd_invite(a):
    _local, shared = require_role("dono")
    if not (shared.get("organizacao") or {}).get("id"):
        raise SystemExit("O escritório ainda não foi iniciado pelo novo fluxo.")
    print(make_invite(shared, a.papel))

def cmd_decode_invite(a):
    invite = read_invite(a.codigo)
    print("ESCRITÓRIO:", invite["escritorio"])
    print("REPOSITÓRIO PRIVADO:", invite["repositorio"])
    print("PAPEL:", invite["papel"])

def cmd_diagnose(_a):
    checks = []
    checks.append((SHARED.exists(), "configuração compartilhada existe"))
    checks.append((LOCAL.exists(), "configuração local existe e está ignorada"))
    try:
        local, shared = config()
        checks += [
            (shared.get("modo") == "mvp", "modo MVP ativo"),
            (shared.get("gates", {}).get("protocolo_manual") is True, "protocolo continua manual"),
            (local_roles(local).issubset(VALID_ROLES) and bool(local_roles(local)), "papel local válido"),
            (local.get("agente") in VALID_AGENTS, "agente local válido"),
            (local.get("repositorio_privado_confirmado") is True, "repositório operacional privado confirmado"),
            (shared.get("conectores", {}).get("sync", {}).get("somente_leitura") is True, "Sync limitado a somente leitura"),
        ]
    except (SystemExit, KeyError, json.JSONDecodeError):
        pass
    ignored = subprocess.run(["git", "check-ignore", "-q", str(LOCAL)], cwd=ROOT).returncode == 0 if (ROOT / ".git").exists() else True
    checks.append((ignored, "segredos/configuração local fora do Git"))
    for ok, label in checks:
        print(("OK" if ok else "FALHA"), "—", label)
    if not all(ok for ok, _ in checks):
        raise SystemExit(1)

def slug(value):
    value = re.sub(r"[^a-zA-Z0-9-]+", "-", value.strip()).strip("-").lower()
    return value or "tarefa"

def cmd_create(a):
    local, shared = require_role("controller")
    if local.get("repositorio_privado_confirmado") is not True:
        raise SystemExit("BLOQUEADO: crie/conecte e confirme o repositório privado antes de registrar tarefas.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    task_id = f"{stamp}-{slug(a.referencia)}"
    data = {"schema_version": 1, "id": task_id, "status": "aberta", "modo": shared["modo"],
            "cnj": a.cnj, "referencia_entrada": a.referencia, "fonte": "sync",
            "providencia_sugerida": a.providencia, "responsavel": a.responsavel,
            "criada_por": local["colaborador"], "criada_em": now(), "entrega": None,
            "revisao": None, "historico": []}
    event(data, "criada", local["colaborador"], "Providência é sugestão sujeita à revisão humana.")
    save(ROOT / "fila" / f"{task_id}.json", data)
    auto_git([f"fila/{task_id}.json"], f"fila: criar {task_id}")
    print(task_id)

def visible(data, local):
    return "controller" in local_roles(local) or not data.get("responsavel") or data.get("responsavel") == local["colaborador"] or data.get("advogado") == local["colaborador"]

def cmd_list(a):
    pull_before_read()
    local, _ = config()
    rows = []
    for p in sorted((ROOT / "fila").glob("*.json")):
        data = load(p)
        if visible(data, local) and (not a.status or data["status"] == a.status):
            rows.append((data["id"], data["status"], data.get("responsavel") or "livre", data["cnj"]))
    print("ID | STATUS | RESPONSÁVEL | CNJ")
    for row in rows:
        print(" | ".join(row))

def cmd_claim(a):
    local, _ = require_role("advogado")
    data = task(a.id)
    if data.get("responsavel") and data["responsavel"] != local["colaborador"]:
        raise SystemExit("Tarefa destinada a outro colaborador.")
    transition(data, "em_execucao")
    data["advogado"] = local["colaborador"]
    event(data, "assumida", local["colaborador"])
    save(task_path(a.id), data)
    auto_git([f"fila/{a.id}.json"], f"fila: assumir {a.id}")
    print("OK — tarefa assumida:", a.id)

def resolve_context(data, local):
    destino = ROOT / ".metodo-euro-contextos" / data["id"] / "entrada"
    try:
        return sync_connector.materializar_entrada(data["cnj"], destino, local["organizacao_id"])
    except RuntimeError as exc:
        raise SystemExit(f"Não foi possível preparar os autos pelo Sync: {exc}")

def cmd_context(a):
    local, _ = require_role("advogado")
    data = task(a.id)
    if data.get("advogado") != local["colaborador"]:
        raise SystemExit("Assuma a tarefa antes de abrir o contexto.")
    path = resolve_context(data, local)
    print("ENTRADA AUTORIZADA:", path)

def cmd_submit(a):
    local, _ = require_role("advogado")
    data = task(a.id)
    if data.get("advogado") != local["colaborador"]:
        raise SystemExit("Tarefa não pertence a este Advogado.")
    source = Path(a.arquivo).expanduser().resolve()
    if not source.is_file():
        raise SystemExit("Arquivo de entrega não encontrado.")
    target_dir = ROOT / "entregas" / a.id
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name
    target.write_bytes(source.read_bytes())
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    transition(data, "entregue")
    data["entrega"] = {"arquivo": str(target.relative_to(ROOT)), "sha256": digest, "em": now(), "por": local["colaborador"]}
    event(data, "entregue", local["colaborador"], f"sha256:{digest}")
    save(task_path(a.id), data)
    auto_git([f"fila/{a.id}.json", f"entregas/{a.id}"], f"fila: entregar {a.id}")
    print("OK — entrega registrada; protocolo não executado. SHA256:", digest)

def cmd_review(a):
    local, _ = require_role("controller")
    data = task(a.id)
    target = {"aprovada": "aprovada", "ajustes": "ajustes", "reprovada": "reprovada"}[a.decisao]
    transition(data, target)
    data["revisao"] = {"decisao": a.decisao, "feedback": a.feedback, "por": local["colaborador"], "em": now()}
    event(data, "revisada", local["colaborador"], a.decisao)
    save(task_path(a.id), data)
    auto_git([f"fila/{a.id}.json"], f"fila: revisar {a.id}")
    print("OK — revisão registrada; aprovação não equivale a protocolo.")

def cmd_reopen(a):
    local, _ = require_role("advogado")
    data = task(a.id)
    if data.get("advogado") != local["colaborador"]:
        raise SystemExit("Tarefa não pertence a este Advogado.")
    transition(data, "em_execucao")
    event(data, "ajustes_iniciados", local["colaborador"])
    save(task_path(a.id), data)
    auto_git([f"fila/{a.id}.json"], f"fila: iniciar ajustes {a.id}")
    print("OK — ajustes iniciados.")

def cmd_propose(a):
    local, _ = config()
    data = task(a.id)
    if data["status"] != "aprovada":
        raise SystemExit("A proposta exige tarefa aprovada.")
    source = Path(a.arquivo).expanduser().resolve()
    if not source.is_file():
        raise SystemExit("Arquivo da proposta não encontrado.")
    content = source.read_text(encoding="utf-8")
    if data["cnj"] in content or data["referencia_entrada"].lower() in content.lower():
        raise SystemExit("A proposta contém identificador do caso; extraia apenas aprendizado reutilizável.")
    name = slug(a.nome)
    target = ROOT / "propostas" / f"{name}--{a.id}.md"
    header = f"---\nskill: {name}\ntarefa_origem: {a.id}\nproposta_por: {local['colaborador']}\nproposta_em: {now()}\n---\n\n"
    target.write_text(header + content, encoding="utf-8")
    auto_git([str(target.relative_to(ROOT))], f"skill: propor {name}")
    print("OK — proposta criada:", target.relative_to(ROOT))

def cmd_promote(a):
    local, _ = require_role("controller")
    proposal = ROOT / "propostas" / a.proposta
    if not proposal.is_file() or proposal.suffix != ".md":
        raise SystemExit("Proposta não encontrada.")
    match = re.search(r"^skill:\s*(.+)$", proposal.read_text(encoding="utf-8"), re.M)
    if not match:
        raise SystemExit("Proposta sem nome de skill.")
    name = slug(match.group(1))
    target = ROOT / "skills" / name / "SKILL.md"
    if target.exists():
        raise SystemExit("Skill já existe; promoção não sobrescreve. Faça proposta de atualização revisável.")
    target.parent.mkdir(parents=True, exist_ok=True)
    body = proposal.read_text(encoding="utf-8")
    target.write_text(f"---\nname: {name}\ndescription: Skill candidata promovida após revisão humana.\n---\n\n" + body, encoding="utf-8")
    auto_git([str(target.relative_to(ROOT))], f"skill: promover {name}")
    print("OK — skill candidata promovida por", local["colaborador"], ":", target.relative_to(ROOT))

def cmd_status(a):
    print(json.dumps(task(a.id), ensure_ascii=False, indent=2))

def cmd_sync(_a):
    if not (ROOT / ".git").exists():
        raise SystemExit("Este diretório ainda não é um clone Git; nada foi sincronizado.")
    remotes = subprocess.run(["git", "remote"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.split()
    if not remotes:
        raise SystemExit("Nenhum remote configurado; trabalho local preservado, nada sincronizado.")
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True, check=True).stdout
    if dirty:
        raise SystemExit("Há alterações locais não commitadas. Preserve-as em commit antes de sincronizar.")
    pull = subprocess.run(["git", "pull", "--rebase"], cwd=ROOT)
    if pull.returncode:
        raise SystemExit("Conflito ou falha no pull. Estado preservado; concilie sem apagar versões.")
    push = subprocess.run(["git", "push"], cwd=ROOT)
    if push.returncode:
        raise SystemExit("Pull concluído, mas push falhou; não declare sincronização completa.")
    print("OK — pull e push concluídos no remote configurado.")

def link_skill(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink() and target.resolve() == source.resolve():
        return "já ligada"
    if target.exists() or target.is_symlink():
        return "preservada (já existia)"
    target.symlink_to(source, target_is_directory=True)
    return "ligada"

def cmd_install_skills(a):
    base = Path(a.destino_base).expanduser().resolve() if a.destino_base else Path.home()
    results = []
    for source in sorted((ROOT / "skills").iterdir()):
        if not source.is_dir() or not (source / "SKILL.md").is_file():
            continue
        for relative in (Path(".claude/skills"), Path(".agents/skills")):
            target = base / relative / source.name
            results.append((target, link_skill(source, target)))
    for target, status in results:
        print("OK —", status, ":", target)

def cmd_prepare_auto_sync(_a):
    runtime = ROOT / ".metodo-euro-runtime"
    runtime.mkdir(exist_ok=True)
    runner = runtime / "auto-sync.py"
    runner.write_text("""#!/usr/bin/env python3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
root = Path(__file__).resolve().parents[1]
log = Path(__file__).with_name('auto-sync.log')
def record(message):
    with log.open('a', encoding='utf-8') as f:
        f.write(datetime.now(timezone.utc).isoformat(timespec='seconds') + ' ' + message + '\\n')
dirty = subprocess.run(['git','status','--porcelain'], cwd=root, text=True, capture_output=True)
if dirty.returncode or dirty.stdout:
    record('BLOQUEADO arvore suja ou Git indisponivel; nada alterado')
    raise SystemExit(0)
fetch = subprocess.run(['git','fetch','origin'], cwd=root)
if fetch.returncode:
    record('FALHA fetch; nada apagado')
    raise SystemExit(fetch.returncode)
pull = subprocess.run(['git','pull','--rebase'], cwd=root)
if pull.returncode:
    subprocess.run(['git','rebase','--abort'], cwd=root)
    record('CONFLITO preservado; rebase abortado para conciliacao')
    raise SystemExit(pull.returncode)
push = subprocess.run(['git','push','origin','HEAD'], cwd=root)
record('OK sincronizado' if push.returncode == 0 else 'FALHA push; commits locais preservados')
raise SystemExit(push.returncode)
""", encoding="utf-8")
    os.chmod(runner, 0o700)
    python = Path(sys.executable).resolve()
    if platform.system() == "Windows":
        task = runtime / "INSTALAR-TAREFA-WINDOWS.ps1"
        task.write_text(f'''$Action = New-ScheduledTaskAction -Execute "{python}" -Argument '"{runner}"'\n$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 10)\nRegister-ScheduledTask -TaskName "MetodoEuroAutoSync" -Action $Action -Trigger $Trigger -Description "Sincroniza o repositorio privado do Metodo Euro" -Force\n''', encoding="utf-8")
        print("OK — execute internamente e valide a tarefa:", task)
    else:
        plist = runtime / "com.metodoeuro.autosync.plist"
        plist.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.metodoeuro.autosync</string>
<key>ProgramArguments</key><array><string>{python}</string><string>{runner}</string></array>
<key>StartInterval</key><integer>600</integer>
<key>RunAtLoad</key><true/>
</dict></plist>
''', encoding="utf-8")
        print("OK — instale internamente no LaunchAgents e valide uma execução:", plist)

def _pedir_chave_sync():
    """Recebe o segredo sem colocá-lo em argumento, Git ou texto da conversa."""
    if os.getenv("METODO_EURO_SYNC_KEY"):
        return os.environ["METODO_EURO_SYNC_KEY"]
    if platform.system() == "Darwin":
        script = 'display dialog "Cole a chave do Sync" default answer "" with hidden answer buttons {"Cancelar", "Salvar"} default button "Salvar"\ntext returned of result'
        result = subprocess.run(["osascript", "-e", script], text=True, capture_output=True)
        if result.returncode:
            raise SystemExit("Configuração do Sync cancelada; nenhuma chave foi salva.")
        return result.stdout.rstrip("\n")
    if platform.system() == "Windows":
        command = "$c=Get-Credential -UserName 'SYNC' -Message 'Cole a chave do Sync no campo de senha'; $c.GetNetworkCredential().Password"
        result = subprocess.run(["powershell", "-NoProfile", "-Command", command], text=True, capture_output=True)
        if result.returncode:
            raise SystemExit("Configuração do Sync cancelada; nenhuma chave foi salva.")
        return result.stdout.rstrip("\r\n")
    return getpass.getpass("Chave do Sync (não será exibida): ")

def cmd_configure_sync(_a):
    local, shared = config()
    if not shared.get("conectores", {}).get("sync", {}).get("somente_leitura"):
        raise SystemExit("BLOQUEADO: o conector não está marcado como somente leitura.")
    chave = _pedir_chave_sync()
    cliente = sync_connector.ClienteSync(chave)
    try:
        conta = cliente.conta()
    except RuntimeError as exc:
        raise SystemExit(f"A chave não foi salva: {exc}")
    if not conta.get("ativo") or not conta.get("acesso_liberado"):
        raise SystemExit("A conta do Sync não está ativa/liberada; a chave não foi salva.")
    sync_connector.salvar_chave(chave, local["organizacao_id"])
    print("OK — Sync conectado em modo somente leitura para:", conta.get("conta") or "conta identificada")
    print("OK — chave guardada somente neste computador, fora do Git e da conversa.")

def cmd_test_sync(_a):
    local, _shared = config()
    try:
        conta = sync_connector.ClienteSync(sync_connector.carregar_chave(local["organizacao_id"])).conta()
    except RuntimeError as exc:
        raise SystemExit(f"FALHA — Sync: {exc}")
    print("OK — leitura do Sync autorizada para:", conta.get("conta") or "conta identificada")

def parser():
    p = argparse.ArgumentParser(description="Kit 2 Método Euro — fila jurídica segura")
    sub = p.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("iniciar-escritorio"); q.add_argument("--nome", required=True); q.add_argument("--escritorio", required=True); q.add_argument("--agente", choices=sorted(VALID_AGENTS), default="claude"); q.add_argument("--repositorio", default=""); q.add_argument("--tambem-controller", action="store_true"); q.set_defaults(fn=cmd_start_office)
    q = sub.add_parser("entrar-com-codigo"); q.add_argument("codigo"); q.add_argument("--nome", required=True); q.add_argument("--agente", choices=sorted(VALID_AGENTS), default="claude"); q.set_defaults(fn=cmd_join)
    q = sub.add_parser("gerar-codigo"); q.add_argument("--papel", choices=["advogado", "controller"], required=True); q.set_defaults(fn=cmd_invite)
    q = sub.add_parser("decodificar-codigo"); q.add_argument("codigo"); q.set_defaults(fn=cmd_decode_invite)
    q = sub.add_parser("configurar"); q.add_argument("--nome", required=True); q.add_argument("--escritorio", required=True); q.add_argument("--papel", choices=sorted(VALID_ROLES), required=True); q.add_argument("--agente", choices=sorted(VALID_AGENTS), required=True); q.add_argument("--repositorio-privado-confirmado", action="store_true", help="Use somente após verificar no GitHub que o repositório operacional é privado."); q.set_defaults(fn=cmd_configure)
    q = sub.add_parser("diagnosticar"); q.set_defaults(fn=cmd_diagnose)
    q = sub.add_parser("criar-tarefa"); q.add_argument("--cnj", required=True); q.add_argument("--referencia", required=True); q.add_argument("--providencia", required=True); q.add_argument("--responsavel", default=""); q.set_defaults(fn=cmd_create)
    q = sub.add_parser("listar"); q.add_argument("--status"); q.set_defaults(fn=cmd_list)
    q = sub.add_parser("assumir"); q.add_argument("id"); q.set_defaults(fn=cmd_claim)
    q = sub.add_parser("contexto"); q.add_argument("id"); q.set_defaults(fn=cmd_context)
    q = sub.add_parser("entregar"); q.add_argument("id"); q.add_argument("arquivo"); q.set_defaults(fn=cmd_submit)
    q = sub.add_parser("revisar"); q.add_argument("id"); q.add_argument("decisao", choices=["aprovada", "ajustes", "reprovada"]); q.add_argument("--feedback", required=True); q.set_defaults(fn=cmd_review)
    q = sub.add_parser("iniciar-ajustes"); q.add_argument("id"); q.set_defaults(fn=cmd_reopen)
    q = sub.add_parser("propor-skill"); q.add_argument("id"); q.add_argument("--nome", required=True); q.add_argument("--arquivo", required=True); q.set_defaults(fn=cmd_propose)
    q = sub.add_parser("promover-skill"); q.add_argument("proposta"); q.set_defaults(fn=cmd_promote)
    q = sub.add_parser("status"); q.add_argument("id"); q.set_defaults(fn=cmd_status)
    q = sub.add_parser("sincronizar"); q.set_defaults(fn=cmd_sync)
    q = sub.add_parser("instalar-skills"); q.add_argument("--destino-base"); q.set_defaults(fn=cmd_install_skills)
    q = sub.add_parser("preparar-auto-sync"); q.set_defaults(fn=cmd_prepare_auto_sync)
    q = sub.add_parser("configurar-sync"); q.set_defaults(fn=cmd_configure_sync)
    q = sub.add_parser("testar-sync"); q.set_defaults(fn=cmd_test_sync)
    return p

if __name__ == "__main__":
    args = parser().parse_args()
    try:
        args.fn(args)
    except KeyboardInterrupt:
        raise SystemExit("Interrompido; estado anterior preservado.")
