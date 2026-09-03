# Kit 2 — Método Euro

Um núcleo único para Controller e Executor, Claude Code e Codex, um ou vários colaboradores. O
repositório privado do escritório é a fonte canônica; cada pessoa usa sua conta pessoal do GitHub e
um clone próprio. O núcleo funciona sem software jurídico:

`Sync/congelado (leitura) → fila GitHub → Controller → Executor → revisão → proposta → skill`

O Infinitum é opcional. O modo inicial é sempre `sandbox` e bloqueia efeitos externos.

## Instalação guiada por um prompt

Abra Claude Code na pasta permanente `Claude` e envie o texto abaixo. O aluno não precisa abrir
Terminal ou PowerShell.

```text
Instale o Kit 2 do Método Euro a partir do repositório informado pelo professor. Leia e audite os
arquivos antes de executar qualquer coisa. Faça tudo por mim usando suas ferramentas internas, sem
me mandar abrir terminal. Confirme que o repositório é privado e peça apenas o login oficial do
GitHub no navegador se for inevitável. Cada pessoa deve usar sua própria conta e seu próprio clone.

Execute o assistente de configuração em modo sandbox. Pergunte meu nome, escritório, papel
(controller ou executor), agente (Claude Code ou Codex) e o caminho local autorizado dos casos.
Não solicite nem grave tokens na conversa ou no Git. Não habilite Infinitum nem escrita em sistema
externo. Ao final, rode o diagnóstico e mostre os checkpoints em linguagem simples.
```

## Fluxo operacional

O assistente executa `python3 euro.py configurar`. Depois:

- `python3 euro.py instalar-skills` liga a fonte canônica aos diretórios reconhecidos por Claude Code
  e Codex, preservando qualquer instalação preexistente.
- `python3 euro.py preparar-auto-sync` cria os arquivos locais para sincronização conservadora a cada
  dez minutos. O Claude instala/ativa o agendamento nativo do sistema e comprova uma execução.

1. Controller: `criar-tarefa`, confere e sincroniza.
2. Executor: `listar`, `assumir ID`, `contexto ID`, produz arquivo e `entregar ID ARQUIVO`.
3. Controller: `revisar ID aprovada|ajustes|reprovada --feedback ...`.
4. Se houver aprendizado reutilizável: `propor-skill`; após revisão, `promover-skill`.

Use `python3 euro.py --help` para os argumentos. `sincronizar` faz pull com rebase e push somente se
o clone tiver remote; em conflito, para e preserva o estado para conciliação humana.

## Checkpoints visuais

- `diagnosticar`: todos os itens críticos aparecem como `OK`.
- `listar`: o Executor vê apenas tarefas destinadas a ele ou ainda disponíveis.
- `contexto`: mostra exatamente uma pasta `entrada`; caminho contendo `gabarito` é recusado.
- `status`: registra autor, horário, transição e hash da entrega.
- `promover-skill`: só aceita proposta de tarefa aprovada e nunca sobrescreve skill existente.

## Escritório real

O Kit inclui apenas contratos de conectores. A promoção para `escritorio` exige edição consciente de
`metodo-euro.json`, revisão dos adaptadores e teste próprio. O Sync permanece somente leitura. Este
Kit não implementa protocolo automático. O adaptador Infinitum é uma interface opcional, não uma
integração ativa nem uma credencial embutida.

## Segurança e contingência

- Nunca versione `.metodo-euro.local.json`, `.env`, autos, minutas reais ou certificados.
- Se o Git estiver indisponível, trabalhe no clone local e não simule que sincronizou.
- Se houver conflito, não apague nenhum lado. O comando para e informa os arquivos.
- O auto-sync só atua com árvore limpa. Alterações ainda não commitadas ficam preservadas e a rodada
  é registrada como bloqueada; o colaborador ou agente deve revisá-las e criar o commit.
- Se um documento estiver ausente, registre a lacuna na minuta e na revisão.
- Para desfazer uma instalação, remova apenas este clone; as configurações e credenciais externas não
  são alteradas pelo Kit.
