#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).parents[1]
required = ["README.md", "AGENTS.md", "CLAUDE.md", "euro.py", "metodo-euro.json",
            "skills/configurar-kit2/SKILL.md", "skills/controller-fila/SKILL.md",
            "skills/executar-tarefa/SKILL.md", "skills/revisar-entrega/SKILL.md",
            "skills/evoluir-skill/SKILL.md", "skills/resumo-do-processo/SKILL.md",
            "skills/gerar-peticao-por-modelo/SKILL.md", "skills/atualizar-kit/SKILL.md",
            "versao-kit.json", "manifesto-arquivos.json",
            "integracoes/infinitum/Instalador-Esteira-Peticoes-Infinitum-v1.0.0.zip",
            "integracoes/infinitum/Instalador-Esteira-Peticoes-Infinitum-v1.0.0.zip.sha256"]
missing = [p for p in required if not (root / p).is_file()]
if missing:
    raise SystemExit("Arquivos ausentes: " + ", ".join(missing))
cfg = json.loads((root / "metodo-euro.json").read_text())
assert cfg["modo"] == "mvp"
assert cfg["conectores"]["sync"]["somente_leitura"] is True
assert cfg["conectores"]["sync"]["obrigatorio_metodo_euro"] is True
assert cfg["fonte_autos"] == "sync"
assert cfg["conectores"]["infinitum"]["habilitado"] is False
assert cfg["gates"]["protocolo_manual"] is True
signatures = ("gh" + "p_", "github" + "_pat_", "sk-" + "ant-", "Bear" + "er ")
for secret in signatures:
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts and path != Path(__file__) and secret in path.read_text(errors="ignore"):
            raise SystemExit(f"Possível segredo em {path}")
result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=root)
raise SystemExit(result.returncode)
