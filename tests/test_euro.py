import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("euro", Path(__file__).parents[1] / "euro.py")
euro = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(euro)
SYNC_SPEC = importlib.util.spec_from_file_location("kit_sync", Path(__file__).parents[1] / "conectores" / "sync.py")
kit_sync = importlib.util.module_from_spec(SYNC_SPEC)
SYNC_SPEC.loader.exec_module(kit_sync)

class EuroTests(unittest.TestCase):
    def test_state_machine_rejects_skip(self):
        data = {"status": "aberta"}
        with self.assertRaises(SystemExit):
            euro.transition(data, "aprovada")

    def test_state_machine_happy_path(self):
        data = {"status": "aberta"}
        for state in ("em_execucao", "entregue", "aprovada"):
            euro.transition(data, state)
        self.assertEqual(data["status"], "aprovada")

    def test_private_confirmation_is_explicit(self):
        parsed = euro.parser().parse_args(["configurar", "--nome", "A", "--escritorio", "E", "--papel", "advogado", "--agente", "claude"])
        self.assertFalse(parsed.repositorio_privado_confirmado)

    def test_invite_round_trip(self):
        shared = {"nome_escritorio": "Escritório Exemplo", "organizacao": {
            "id": "org-1", "controller": "Pessoa Um", "repositorio": "https://github.com/exemplo/privado"}}
        code = euro.make_invite(shared, "controller")
        decoded = euro.read_invite(code)
        self.assertEqual(decoded["escritorio"], "Escritório Exemplo")
        self.assertEqual(decoded["papel"], "controller")

    def test_owner_can_accumulate_controller(self):
        parsed = euro.parser().parse_args(["iniciar-escritorio", "--nome", "A", "--escritorio", "E", "--tambem-controller"])
        self.assertTrue(parsed.tambem_controller)

    def test_invite_requires_specific_role(self):
        parsed = euro.parser().parse_args(["gerar-codigo", "--papel", "advogado"])
        self.assertEqual(parsed.papel, "advogado")

    def test_sync_materializes_chronology_and_markdown_locally(self):
        class FakeSync:
            def autos(self, _cnj):
                return {"total": 2, "capa": {}, "autos": [
                    {"tipo": "movimento", "data": "2026-01-01", "descricao": "Despacho"},
                    {"tipo": "documento", "data": "2026-01-02", "id": 7,
                     "nome": "decisão.pdf", "tipo_documento": "Decisão", "tem_markdown": True},
                ]}
            def markdown(self, documento_id):
                return f"# Documento {documento_id}\n"
        with tempfile.TemporaryDirectory() as d:
            entrada = kit_sync.materializar_entrada("000", Path(d) / "entrada", "org", FakeSync())
            self.assertTrue((entrada / "0000-CRONOLOGIA.md").is_file())
            self.assertEqual(len(list(entrada.glob("*7*.md"))), 1)
            manifesto = json.loads((entrada / "manifesto-sync.json").read_text())
            self.assertEqual(manifesto["total"], 2)

    def test_tampered_invite_is_rejected(self):
        shared = {"nome_escritorio": "E", "organizacao": {"id": "1", "repositorio": "https://example.invalid/r"}}
        code = euro.make_invite(shared)
        with self.assertRaises(SystemExit):
            euro.read_invite(code + "x")

    def test_skill_link_preserves_existing(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "source"; source.mkdir()
            target = Path(d) / "target"; target.mkdir()
            self.assertIn("preservada", euro.link_skill(source, target))

    def test_skill_link_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "source"; source.mkdir()
            target = Path(d) / "target"
            self.assertEqual(euro.link_skill(source, target), "ligada")
            self.assertEqual(euro.link_skill(source, target), "já ligada")

if __name__ == "__main__":
    unittest.main()
