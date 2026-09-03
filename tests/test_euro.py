import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("euro", Path(__file__).parents[1] / "euro.py")
euro = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(euro)

class EuroTests(unittest.TestCase):
    def test_gabarito_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "caso" / "gabarito" / "entrada"
            p.mkdir(parents=True)
            with self.assertRaises(SystemExit):
                euro.safe_input_path(p)

    def test_only_existing_entrada_is_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "caso" / "entrada"
            p.mkdir(parents=True)
            self.assertEqual(euro.safe_input_path(p), p.resolve())

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
