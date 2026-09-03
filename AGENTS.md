# Método Euro — regras para Claude Code e Codex

Este repositório é a fonte canônica compartilhada de regras, skills e fila. Leia `README.md`,
`metodo-euro.json` e a configuração local antes de agir.

O repositório público do Kit é apenas um molde. Nunca grave tarefa, CNJ, nome ou documento nele.
Antes de operar, crie/conecte um repositório privado do escritório e registre essa confirmação na
configuração local. Sem a confirmação, `criar-tarefa` deve permanecer bloqueado.

- Comece sempre em `sandbox`. Nesse modo, não escreva no Sync, Infinitum, Esteira, Meu Estagiário,
  processo vivo ou qualquer sistema externo.
- Autos são somente leitura. Nunca protocole. Revisão humana e protocolo são gates distintos.
- O primeiro instalador é `dono`; somente ele nomeia Controllers e ele pode acumular `controller`.
- O papel `controller` cria, distribui e revisa tarefas; `advogado` assume e entrega tarefas.
- O Advogado usa apenas a entrada resolvida pelo comando `contexto`; nunca procure nem abra gabaritos.
- Segredos ficam na máquina, fora do Git e fora da conversa.
- Sincronize antes e depois de alterar a fila. Se houver conflito, preserve as duas versões e peça
  conciliação; nunca resolva apagando trabalho.
- Uma revisão não muda uma skill automaticamente. Registre a proposta; somente o Controller promove
  aprendizado reutilizável após distinguir erro de execução, deficiência da skill e peculiaridade.
- Em caso de dúvida factual, declare a lacuna. Não invente movimento, documento, prazo ou estratégia.

As mesmas regras valem no Claude Code (`CLAUDE.md`) e no Codex (`AGENTS.md`).
