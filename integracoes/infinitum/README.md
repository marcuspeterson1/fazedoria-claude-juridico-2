# Instalador portátil — Infinitum

Este diretório incorpora, sem modificar, o artefato `v1.0.0` já testado da Esteira de Petições para
o Infinitum. O arquivo `.sha256` permite provar sua integridade.

O Claude deve descompactar o ZIP numa pasta temporária, ler integralmente `LEIA-ME.md`,
`INSTRUCOES_AGENTE.md`, `manifesto.json`, `CONTRATO_DO_WORKER.md`, `AGENTS.md`, `CLAUDE.md` e
`instalar.py`, e somente então seguir a instalação. O aluno não monta fases ou campos manualmente.

Antes de qualquer acesso, explique de forma simples:

- o Infinitum é o armário onde as tarefas serão organizadas;
- a API é uma porta para o Claude organizar esse armário;
- o token é a chave dessa porta e deve ficar escondido no computador;
- o instalador monta o armário, mas o worker jurídico é quem depois produz as minutas.

Nunca peça que o aluno cole o token no chat. Use sessão autenticada em navegador controlável ou
secret store/arquivo local protegido. A instalação pode criar estruturas e teste sintético na conta
escolhida, mas não pode apagar, arquivar ou usar dados reais. Só conclua com
`resultado_instalacao.json` aprovado e protocolo ainda manual.
