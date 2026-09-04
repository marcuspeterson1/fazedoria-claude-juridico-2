import importlib.util
import json
import tempfile
import unittest
import contextlib
import io
import os
from pathlib import Path
from unittest import mock

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

    def test_document_policy_is_owner_command(self):
        parsed = euro.parser().parse_args(["configurar-documentos", "--onde-modelos", "Drive", "--pastas-clientes", "sim", "--destino-copia", "Pasta do cliente", "--padrao-nomes", "TIPO - CLIENTE"])
        self.assertEqual(parsed.onde_modelos, "Drive")

    def test_delivery_requires_model_traceability(self):
        with self.assertRaises(SystemExit):
            euro.parser().parse_args(["entregar", "tarefa", "minuta.docx"])

    def test_daily_card_is_role_specific(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            euro.print_daily_card({"papel": "advogado", "papeis": ["advogado"]})
        self.assertIn("/executar-tarefa", out.getvalue())
        self.assertNotIn("/controller-fila", out.getvalue())

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
            self.assertTrue(manifesto["leitura_integral_confirmada"])

    def test_sync_manifest_blocks_integral_confirmation_when_document_is_unavailable(self):
        class FakeSync:
            def autos(self, _cnj):
                return {"total": 1, "capa": {}, "autos": [
                    {"tipo": "documento", "data": "2026-01-02", "id": 8,
                     "nome": "anexo.pdf", "tipo_documento": "Anexo", "tem_markdown": False},
                ]}
        with tempfile.TemporaryDirectory() as d:
            entrada = kit_sync.materializar_entrada("000", Path(d) / "entrada", "org", FakeSync())
            manifesto = json.loads((entrada / "manifesto-sync.json").read_text())
            self.assertFalse(manifesto["leitura_integral_confirmada"])
            self.assertEqual(len(manifesto["indisponiveis"]), 1)

    def test_existing_secure_env_file_can_be_reused(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / ".secrets.env"
            path.write_text("ATENDE_DIREITO_SYNC_KEY='valor-local'\n", encoding="utf-8")
            self.assertEqual(kit_sync._ler_env(path)["ATENDE_DIREITO_SYNC_KEY"], "valor-local")

    def test_general_claude_config_is_never_scanned_for_sync_key(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            (home / ".claude").mkdir()
            (home / ".claude" / "settings.json").write_text(
                '{"url":"https://sync.atendedireito.app","token":"sk_outra_integracao"}',
                encoding="utf-8")
            with mock.patch.object(kit_sync.Path, "home", return_value=home), mock.patch.dict(os.environ, {}, clear=True):
                self.assertEqual(kit_sync.descobrir_chave_existente("org"), (None, None))

    def test_windows_subprocesses_are_hidden(self):
        with mock.patch.object(euro.platform, "system", return_value="Windows"):
            self.assertIn("creationflags", euro.hidden_subprocess_kwargs())

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
