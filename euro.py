#!/usr/bin/env python3
"""CLI sem dependências do Kit 2 Método Euro."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import platform
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOCAL = ROOT / ".metodo-euro.local.json"
SHARED = ROOT / "metodo-euro.json"
VALID_ROLES = {"controller", "advogado"}
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

def config():
    if not LOCAL.exists():
        raise SystemExit("Configuração local ausente. Execute: python3 euro.py configurar")
    return load(LOCAL), load(SHARED)

def require_role(expected):
    local, shared = config()
    if local["papel"] != expected:
        raise SystemExit(f"Ação exclusiva de {expected}; papel local: {local['papel']}")
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

def safe_input_path(path):
    resolved = Path(path).expanduser().resolve()
    if "gabarito" in {part.lower() for part in resolved.parts}:
        raise SystemExit("BLOQUEADO: o Advogado não pode abrir caminho de gabarito.")
    if resolved.name != "entrada" or not resolved.is_dir():
        raise SystemExit("Entrada inválida: o caminho deve terminar em uma pasta existente chamada 'entrada'.")
    return resolved

def cmd_configure(a):
    if a.papel not in VALID_ROLES or a.agente not in VALID_AGENTS:
        raise SystemExit("Papel ou agente inválido.")
    roots = {}
    if a.raiz_entradas:
        root = Path(a.raiz_entradas).expanduser().resolve()
        if not root.is_dir():
            raise SystemExit("Raiz de entradas não existe.")
        roots["congelado"] = str(root)
    data = {"schema_version": 1, "colaborador": a.nome, "papel": a.papel,
            "agente": a.agente, "repositorio_privado_confirmado": a.repositorio_privado_confirmado,
            "raizes_entrada": roots, "configurado_em": now()}
    save(LOCAL, data)
    shared = load(SHARED)
    if shared["nome_escritorio"] == "CONFIGURE-ME" and a.escritorio:
        shared["nome_escritorio"] = a.escritorio
        save(SHARED, shared)
    print("OK — configuração local salva fora do Git; modo compartilhado:", shared["modo"])

def cmd_diagnose(_a):
    checks = []
    checks.append((SHARED.exists(), "configuração compartilhada existe"))
    checks.append((LOCAL.exists(), "configuração local existe e está ignorada"))
    try:
        local, shared = config()
        checks += [
            (shared.get("modo") == "sandbox", "modo sandbox ativo"),
            (shared.get("gates", {}).get("protocolo_manual") is True, "protocolo continua manual"),
            (local.get("papel") in VALID_ROLES, "papel local válido"),
            (local.get("agente") in VALID_AGENTS, "agente local válido"),
            (local.get("repositorio_privado_confirmado") is True, "repositório operacional privado confirmado"),
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
    if shared["modo"] != "sandbox" and a.fonte == "congelado":
        raise SystemExit("Fonte congelada é destinada ao sandbox.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    task_id = f"{stamp}-{slug(a.referencia)}"
    data = {"schema_version": 1, "id": task_id, "status": "aberta", "modo": shared["modo"],
            "cnj": a.cnj, "referencia_entrada": a.referencia, "fonte": a.fonte,
            "providencia_sugerida": a.providencia, "responsavel": a.responsavel,
            "criada_por": local["colaborador"], "criada_em": now(), "entrega": None,
            "revisao": None, "historico": []}
    event(data, "criada", local["colaborador"], "Providência é sugestão sujeita à revisão humana.")
    save(ROOT / "fila" / f"{task_id}.json", data)
    print(task_id)

def visible(data, local):
    return local["papel"] == "controller" or not data.get("responsavel") or data.get("responsavel") == local["colaborador"] or data.get("advogado") == local["colaborador"]

def cmd_list(a):
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
    print("OK — tarefa assumida:", a.id)

def resolve_context(data, local):
    if data["fonte"] != "congelado":
        raise SystemExit("Fonte externa requer conector próprio; nenhum acesso foi executado.")
    root = local.get("raizes_entrada", {}).get("congelado")
    if not root:
        raise SystemExit("Raiz local das entradas congeladas não configurada.")
    return safe_input_path(Path(root) / data["referencia_entrada"] / "entrada")

def cmd_context(a):
    local, _ = require_role("advogado")
    data = task(a.id)
    if data.get("advogado") != local["colaborador"]:
        raise SystemExit("Assuma a tarefa antes de abrir o contexto.")
    path = resolve_context(data, local)
    print("ENTRADA AUTORIZADA:", path)
    print("GABARITO: BLOQUEADO até entrega e revisão")

def cmd_submit(a):
    local, _ = require_role("advogado")
    data = task(a.id)
    if data.get("advogado") != local["colaborador"]:
        raise SystemExit("Tarefa não pertence a este Advogado.")
    source = Path(a.arquivo).expanduser().resolve()
    if not source.is_file():
        raise SystemExit("Arquivo de entrega não encontrado.")
    if "gabarito" in {part.lower() for part in source.parts}:
        raise SystemExit("Entrega não pode vir do gabarito.")
    target_dir = ROOT / "entregas" / a.id
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name
    target.write_bytes(source.read_bytes())
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    transition(data, "entregue")
    data["entrega"] = {"arquivo": str(target.relative_to(ROOT)), "sha256": digest, "em": now(), "por": local["colaborador"]}
    event(data, "entregue", local["colaborador"], f"sha256:{digest}")
    save(task_path(a.id), data)
    print("OK — entrega registrada; protocolo não executado. SHA256:", digest)

def cmd_review(a):
    local, _ = require_role("controller")
    data = task(a.id)
    target = {"aprovada": "aprovada", "ajustes": "ajustes", "reprovada": "reprovada"}[a.decisao]
    transition(data, target)
    data["revisao"] = {"decisao": a.decisao, "feedback": a.feedback, "por": local["colaborador"], "em": now()}
    event(data, "revisada", local["colaborador"], a.decisao)
    save(task_path(a.id), data)
    print("OK — revisão registrada; aprovação não equivale a protocolo.")

def cmd_reopen(a):
    local, _ = require_role("advogado")
    data = task(a.id)
    if data.get("advogado") != local["colaborador"]:
        raise SystemExit("Tarefa não pertence a este Advogado.")
    transition(data, "em_execucao")
    event(data, "ajustes_iniciados", local["colaborador"])
    save(task_path(a.id), data)
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

def parser():
    p = argparse.ArgumentParser(description="Kit 2 Método Euro — fila jurídica segura")
    sub = p.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("configurar"); q.add_argument("--nome", required=True); q.add_argument("--escritorio", required=True); q.add_argument("--papel", choices=sorted(VALID_ROLES), required=True); q.add_argument("--agente", choices=sorted(VALID_AGENTS), required=True); q.add_argument("--raiz-entradas"); q.add_argument("--repositorio-privado-confirmado", action="store_true", help="Use somente após verificar no GitHub que o repositório operacional é privado."); q.set_defaults(fn=cmd_configure)
    q = sub.add_parser("diagnosticar"); q.set_defaults(fn=cmd_diagnose)
    q = sub.add_parser("criar-tarefa"); q.add_argument("--cnj", required=True); q.add_argument("--referencia", required=True); q.add_argument("--providencia", required=True); q.add_argument("--responsavel", default=""); q.add_argument("--fonte", choices=["congelado", "sync"], default="congelado"); q.set_defaults(fn=cmd_create)
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
    return p

if __name__ == "__main__":
    args = parser().parse_args()
    try:
        args.fn(args)
    except KeyboardInterrupt:
        raise SystemExit("Interrompido; estado anterior preservado.")
