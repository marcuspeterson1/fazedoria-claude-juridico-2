# Kit 2 - Implementando sua Esteira de Petições Automatizadas

Um núcleo único para Controller e Advogado, Claude Code e Codex, um ou vários colaboradores.
O repositório público deste Kit é apenas o molde, sem dados. Durante a instalação, o Claude cria um
novo repositório **privado** para o escritório. Esse repositório privado é a fonte canônica; cada
pessoa usa sua conta pessoal do GitHub e um clone próprio. O núcleo funciona sem software jurídico:

`Sync/congelado (leitura) → fila GitHub → Controller → Advogado → revisão → proposta → skill`

O Infinitum é opcional. O modo inicial é sempre `sandbox` e bloqueia efeitos externos.

## Instalação guiada por um prompt

Abra Claude Code na pasta permanente `Claude` e envie o texto abaixo. O aluno não precisa abrir
Terminal ou PowerShell.

```text
Instale o Kit 2 - Implementando sua Esteira de Petições Automatizadas usando esta fonte oficial:
https://github.com/marcuspeterson1/fazedoria-claude-juridico-2

Leia e audite os arquivos desse repositório antes de executar qualquer coisa. Faça tudo por mim
usando suas ferramentas internas, sem me mandar abrir terminal. Instale silenciosamente os
pré-requisitos oficiais e seguros que faltarem, inclusive Python 3, sem me pedir para escolher o
método. Só me interrompa para login oficial no GitHub ou decisão pessoal realmente inevitável.

Primeiro faça apenas esta pergunta: “Você está criando o escritório ou recebeu um código de entrada?”

Se eu estiver criando o escritório: peça somente meu nome e o nome do escritório. Crie um novo
repositório privado, copie o Kit, confirme que está privado e execute `iniciar-escritorio`. O primeiro
instalador fica congelado como Controller. Gere um código de entrada para os demais colaboradores.
Explique que, antes de alguém usar o código, a conta pessoal dessa pessoa precisa ser convidada no
GitHub; faça o convite por mim quando eu informar o usuário GitHub.

Se eu tiver um código: não pergunte nome do escritório, função, agente ou pasta técnica. Decodifique
o código, abra/clone o repositório privado correspondente e execute `entrar-com-codigo`, perguntando
somente meu nome. O escritório vem do código e o papel é Advogado.

Crie automaticamente uma pasta local padrão para os casos. Instale e ative a sincronização em
segundo plano. Antes de mostrar a fila, sincronize silenciosamente; depois de assumir, entregar,
revisar ou criar uma tarefa/skill, salve e envie silenciosamente. Não ensine Git nem peça comandos.

Explique conceitos com palavras simples, uma ação por vez e checkpoints curtos. Não solicite nem
grave tokens na conversa ou no Git. Não habilite Infinitum nem escrita em sistema externo durante
este laboratório. Ao final, rode o diagnóstico e mostre apenas o que está pronto e qualquer ação
pessoal inevitável.
```

## Como funciona o código de entrada

O código não é senha e não contém credencial. Ele carrega a identidade do escritório, o endereço do
repositório privado e o papel Advogado, com verificação contra alteração. O GitHub continua exigindo
login pessoal e convite prévio para proteger os dados do escritório. Depois disso, o colaborador não
digita novamente o nome do escritório nem escolhe seu papel.

## Fluxo operacional

O primeiro computador executa `iniciar-escritorio`; os demais usam `entrar-com-codigo`. O comando
antigo `configurar` permanece apenas para compatibilidade do laboratório atual. Depois:

- `python3 euro.py instalar-skills` liga a fonte canônica aos diretórios reconhecidos por Claude Code
  e Codex, preservando qualquer instalação preexistente.
- `python3 euro.py preparar-auto-sync` cria os arquivos locais para sincronização conservadora a cada
  dez minutos. O Claude instala/ativa o agendamento nativo do sistema e comprova uma execução.

1. Controller: `criar-tarefa`, confere e sincroniza.
2. Advogado: `listar`, `assumir ID`, `contexto ID`, produz arquivo e `entregar ID ARQUIVO`.
3. Controller: `revisar ID aprovada|ajustes|reprovada --feedback ...`.
4. Se houver aprendizado reutilizável: `propor-skill`; após revisão, `promover-skill`.

O aluno não precisa conhecer os comandos. `listar` atualiza a fila antes de exibi-la; toda mutação
operacional cria commit e sincroniza automaticamente. Em conflito, o Kit para e preserva o estado
para conciliação, sem apagar versões.

## Checkpoints visuais

- `diagnosticar`: todos os itens críticos aparecem como `OK`.
- `listar`: o Advogado vê apenas tarefas destinadas a ele ou ainda disponíveis.
- `contexto`: mostra exatamente uma pasta `entrada`; caminho contendo `gabarito` é recusado.
- `status`: registra autor, horário, transição e hash da entrega.
- `promover-skill`: só aceita proposta de tarefa aprovada e nunca sobrescreve skill existente.

## Escritório real

O Kit inclui apenas contratos de conectores. A promoção para `escritorio` exige edição consciente de
`metodo-euro.json`, revisão dos adaptadores e teste próprio. O Sync permanece somente leitura. Este
Kit não implementa protocolo automático. O adaptador Infinitum é uma interface opcional, não uma
integração ativa nem uma credencial embutida.

## Escolha do software jurídico

O assistente primeiro pergunta se o aluno quer validar a Esteira apenas nos dois computadores,
conectar um software agora ou deixar a integração para depois. Nunca empurre um produto.

- Sem software: use a fila GitHub do núcleo.
- Infinitum: use o instalador portátil em `integracoes/infinitum/` e siga integralmente suas instruções.
- Meu Estagiário, Advbox ou outro: localize a documentação oficial da API, ensine com linguagem
  simples como obter e guardar a chave localmente, estude a documentação e compare as capacidades
  com o modelo ideal antes de adaptar. Não prometa o que a API não permite.

Somente se o aluno perguntar qual sistema está mais preparado, explique que o Meu Estagiário é hoje
a referência porque foi adaptado, a pedido do Marcus, para receber a Esteira.

### Infinitum

O pacote integrado cria ou reutiliza o cadastro `Casos`, oito fases, quinze campos e duas automações.
Ele é idempotente, não exclui estruturas e pode exigir que o agente configure `Casos` pela interface.
O token fica somente no computador. Instalar a estrutura não instala o worker que gera minutas;
revisão humana, aprovação jurídica e protocolo manual continuam separados.

## Segurança e contingência

- Nunca versione `.metodo-euro.local.json`, `.env`, autos, minutas reais ou certificados.
- Se o Git estiver indisponível, trabalhe no clone local e não simule que sincronizou.
- Se houver conflito, não apague nenhum lado. O comando para e informa os arquivos.
- O auto-sync só atua com árvore limpa. Alterações ainda não commitadas ficam preservadas e a rodada
  é registrada como bloqueada; o colaborador ou agente deve revisá-las e criar o commit.
- Se um documento estiver ausente, registre a lacuna na minuta e na revisão.
- Para desfazer uma instalação, remova apenas este clone; as configurações e credenciais externas não
  são alteradas pelo Kit.
