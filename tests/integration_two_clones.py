#!/usr/bin/env python3
"""Ensaio determinístico de dois computadores; não lê qualquer pasta gabarito."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).parents[1]
os.environ["METODO_EURO_NO_AUTO_GIT"] = "1"
CASES = [
    ("01-caso-nascimento", "0000001-00.2099.0.00.0001", "criar primeira minuta e skill candidata"),
    ("02-caso-validacao", "0000002-00.2099.0.00.0002", "validar invariantes e variáveis"),
    ("03-caso-fronteira", "0000003-00.2099.0.00.0003", "testar fronteira sem reabrir mérito"),
]

def run(cwd, *args, capture=False):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=capture)
    if result.returncode:
        print(result.stdout, result.stderr, file=sys.stderr)
        raise SystemExit(f"Falhou em {cwd}: {' '.join(args)}")
    return result.stdout.strip() if capture else ""

def git(cwd, *args):
    return run(cwd, "git", *args, capture=True)

with tempfile.TemporaryDirectory(prefix="metodo-euro-ensaio-") as tmp:
    base = Path(tmp)
    lab = base / "laboratorio-sintetico"
    for ref, _cnj, _providencia in CASES:
        entrada = lab / ref / "entrada"
        entrada.mkdir(parents=True)
        (entrada / "LEIA-ME.md").write_text("Fixture sintética sem dado de cliente.\n", encoding="utf-8")
    seed = base / "seed"
    shutil.copytree(SOURCE, seed, ignore=shutil.ignore_patterns(".git", "__pycache__", ".metodo-euro.local.json"))
    git(seed, "init", "-b", "main")
    git(seed, "config", "user.name", "Professor Seed")
    git(seed, "config", "user.email", "seed@example.invalid")
    git(seed, "add", ".")
    git(seed, "commit", "-m", "kit 2 base")
    bare = base / "privado.git"
    git(base, "clone", "--bare", str(seed), str(bare))
    controller, executor = base / "mac-controller", base / "notebook-executor"
    git(base, "clone", str(bare), str(controller))
    git(base, "clone", str(bare), str(executor))
    for clone, name, email in ((controller, "Marcus Controller", "controller@example.invalid"),
                               (executor, "Advogada Dois", "advogada@example.invalid")):
        git(clone, "config", "user.name", name); git(clone, "config", "user.email", email)
    run(controller, sys.executable, "euro.py", "configurar", "--nome", "Marcus", "--escritorio", "Laboratório Método Euro", "--papel", "controller", "--agente", "claude", "--raiz-entradas", str(lab), "--repositorio-privado-confirmado")
    git(controller, "add", "metodo-euro.json"); git(controller, "commit", "-m", "configura escritório sandbox"); git(controller, "push")
    git(executor, "pull", "--rebase")
    run(executor, sys.executable, "euro.py", "configurar", "--nome", "Advogada Dois", "--escritorio", "Laboratório Método Euro", "--papel", "advogado", "--agente", "claude", "--raiz-entradas", str(lab), "--repositorio-privado-confirmado")
    links = base / "perfis"
    run(executor, sys.executable, "euro.py", "instalar-skills", "--destino-base", str(links))
    if not (links / ".claude/skills/executar-tarefa/SKILL.md").is_file() or not (links / ".agents/skills/executar-tarefa/SKILL.md").is_file():
        raise SystemExit("Skills não ficaram disponíveis aos dois agentes.")
    run(executor, sys.executable, "euro.py", "preparar-auto-sync")
    if not (executor / ".metodo-euro-runtime/auto-sync.py").is_file():
        raise SystemExit("Runner de auto-sync não foi preparado.")
    run(controller, sys.executable, "euro.py", "diagnosticar")
    run(executor, sys.executable, "euro.py", "diagnosticar")

    task_ids = []
    for index, (ref, cnj, providencia) in enumerate(CASES, 1):
        task_id = run(controller, sys.executable, "euro.py", "criar-tarefa", "--cnj", cnj, "--referencia", ref, "--providencia", providencia, "--responsavel", "Advogada Dois", capture=True)
        task_ids.append(task_id)
        git(controller, "add", "fila"); git(controller, "commit", "-m", f"fila: caso {index}"); git(controller, "push")
        git(executor, "pull", "--rebase")
        run(executor, sys.executable, "euro.py", "assumir", task_id)
        context = run(executor, sys.executable, "euro.py", "contexto", task_id, capture=True)
        if "gabarito" not in context.lower() or "BLOQUEADO" not in context:
            raise SystemExit("Gate de gabarito não ficou explícito.")
        draft = base / f"minuta-{index}.md"
        draft.write_text(f"<!-- SIMULAÇÃO: NÃO PROTOCOLAR -->\n# Rodada {index}\n\nProvidência sugerida sujeita a revisão: {providencia}.\n", encoding="utf-8")
        run(executor, sys.executable, "euro.py", "entregar", task_id, str(draft))
        git(executor, "add", "fila", "entregas"); git(executor, "commit", "-m", f"executor: entrega caso {index}"); git(executor, "push")
        git(controller, "pull", "--rebase")
        run(controller, sys.executable, "euro.py", "revisar", task_id, "aprovada", "--feedback", f"Rodada {index} aprovada apenas para validar o fluxo técnico do laboratório.")
        git(controller, "add", "fila"); git(controller, "commit", "-m", f"controller: revisa caso {index}"); git(controller, "push")
        git(executor, "pull", "--rebase")
        if index == 1:
            proposal = base / "skill-candidata.md"
            proposal.write_text("# Método\n\nIdentificar o ato, conferir se já houve réplica e escolher entre impugnação completa ou manifestação curta. Manter revisão humana.\n", encoding="utf-8")
            run(executor, sys.executable, "euro.py", "propor-skill", task_id, "--nome", "manifestacao-pos-contestacao", "--arquivo", str(proposal))
            git(executor, "add", "propostas"); git(executor, "commit", "-m", "skill: propõe candidata após caso 1"); git(executor, "push")
            git(controller, "pull", "--rebase")
            proposal_name = next((controller / "propostas").glob("manifestacao-pos-contestacao--*.md")).name
            run(controller, sys.executable, "euro.py", "promover-skill", proposal_name)
            git(controller, "add", "skills"); git(controller, "commit", "-m", "skill: promove candidata revisada"); git(controller, "push")
            git(executor, "pull", "--rebase")

    for clone in (controller, executor):
        if git(clone, "status", "--porcelain"):
            raise SystemExit(f"Clone terminou sujo: {clone}")
        if git(clone, "rev-parse", "HEAD") != git(clone, "rev-parse", "origin/main"):
            raise SystemExit(f"Clone não alinhado ao remote: {clone}")
    states = [json.loads((controller / "fila" / f"{task_id}.json").read_text())["status"] for task_id in task_ids]
    if states != ["aprovada"] * 3:
        raise SystemExit(f"Estados finais inesperados: {states}")
    print("ENSAIO OK — 2 clones, 2 identidades, 3 casos aprovados no fluxo técnico, 1 skill candidata promovida.")
    print("GABARITOS NÃO LIDOS — o ensaio acessou somente as três pastas entrada.")
