# Método Euro — regras para Claude Code e Codex

Este repositório é a fonte canônica compartilhada de regras, skills e fila. Leia `README.md`,
`metodo-euro.json` e a configuração local antes de agir.

O repositório público do Kit é apenas um molde. Nunca grave tarefa, CNJ, nome ou documento nele.
Antes de operar, crie/conecte um repositório privado do escritório e registre essa confirmação na
configuração local. Sem a confirmação, `criar-tarefa` deve permanecer bloqueado.

- Comece sempre em `mvp`. O Sync é a fonte obrigatória de autos do Método Euro e permanece
  estritamente em leitura; nesse modo, não escreva no Sync, Infinitum, Esteira, Meu Estagiário,
  processo vivo ou qualquer sistema externo.
- A trava de leitura vale também para integrações antigas já instaladas na máquina. Nunca marque
  intimação como tratada, altere monitoramento, acuse ciência, crie registro ou reutilize uma rotina
  de escrita de outra esteira. "Mostrar intimações" significa somente ler e apresentar.
- Autos são somente leitura. Nunca protocole. Revisão humana e protocolo são gates distintos.
- O primeiro instalador é `dono`; somente ele nomeia Controllers e ele pode acumular `controller`.
- O papel `controller` cria, distribui e revisa tarefas; `advogado` assume e entrega tarefas.
- O Advogado usa apenas a entrada resolvida pelo comando `contexto`, materializada localmente pelo Sync.
- Segredos ficam na máquina, fora do Git e fora da conversa.
- Sincronize antes e depois de alterar a fila. Se houver conflito, preserve as duas versões e peça
  conciliação; nunca resolva apagando trabalho.
- Uma revisão não muda uma skill automaticamente. Registre a proposta; somente o Controller promove
  aprendizado reutilizável após distinguir erro de execução, deficiência da skill e peculiaridade.
- Em caso de dúvida factual, declare a lacuna. Não invente movimento, documento, prazo ou estratégia.
- Antes de concluir uma análise, confira o manifesto do Sync e todos os documentos e anexos do evento
  relevante. Se houver item indisponível ou não lido que possa mudar a tese, pare e declare a lacuna.
- Toda petição nasce de uma cópia de modelo aprovado do escritório. Use `gerar-peticao-por-modelo`;
  nunca redija em documento vazio nem altere o modelo-mãe. Sem modelo, peça que o usuário indique ou
  envie um antes de redigir.
- Evidência inserida pelo advogado (imagem, print, quadro, citação ou marcação) é conteúdo protegido:
  investigue sua origem antes de alterar e nunca a remova silenciosamente. Preserve também versões
  anteriores; só apague ou mova rascunhos com ordem expressa.
- Se este Kit já estiver configurado e o usuário repetir um prompt de instalação, use `atualizar-kit`:
  aplique somente novidades oficiais e preserve identidade, fila, entregas, skills locais e segredos.

As mesmas regras valem no Claude Code (`CLAUDE.md`) e no Codex (`AGENTS.md`).
