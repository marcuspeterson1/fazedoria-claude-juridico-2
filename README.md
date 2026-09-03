# Kit 2 - Implementando sua Esteira de Petições Automatizadas

Um núcleo único para Dono/Administrador, Controller e Advogado, Claude Code e Codex.
O repositório público deste Kit é apenas o molde, sem dados. Durante a instalação, o Claude cria um
novo repositório **privado** para o escritório. Esse repositório privado é a fonte canônica; cada
pessoa usa sua conta pessoal do GitHub e um clone próprio. O núcleo funciona sem software jurídico:

`Sync/congelado (leitura) → fila GitHub → Controller → Advogado → revisão → proposta → skill`

O Infinitum é opcional. O modo inicial é sempre `sandbox` e bloqueia efeitos externos.

## Instalação guiada — dois prompts

O Dono instala primeiro e gera o código. Depois entrega ao colaborador o segundo prompt, substituindo
`SEU_CODIGO_ENTRADA` pelo código gerado. Cada pessoa envia um único prompt ao Claude Code na pasta
permanente `Claude`; ninguém precisa abrir Terminal ou PowerShell.

### Prompt 1 — Dono/Administrador

```text
Instale o Kit 2 - Implementando sua Esteira de Petições Automatizadas usando esta fonte oficial:
https://github.com/marcuspeterson1/fazedoria-claude-juridico-2

Leia e audite os arquivos desse repositório antes de executar qualquer coisa. Faça tudo por mim
usando suas ferramentas internas, sem me mandar abrir terminal. Instale silenciosamente os
pré-requisitos oficiais e seguros que faltarem, inclusive Python 3, sem me pedir para escolher o
método. Só me interrompa para login oficial no GitHub ou decisão pessoal realmente inevitável.

Estou criando o escritório. Peça somente meu nome e o nome do escritório. Crie um novo repositório
privado, copie o Kit, confirme no GitHub que está privado e execute `iniciar-escritorio`. Registre-me
como Dono/Administrador e pergunte se também trabalharei como Controller.

Ao final, pergunte se quero gerar código para Controller ou Advogado. Somente o Dono pode gerar esses
códigos. Entregue o código e o Prompt 2 completo já com `SEU_CODIGO_ENTRADA` substituído. Explique que,
quando o Claude do colaborador identificar o usuário GitHub dele, eu deverei informar esse usuário
aqui para você enviar o convite ao repositório privado.

Crie automaticamente uma pasta local padrão para os casos. Instale e ative a sincronização em
segundo plano. Antes de mostrar a fila, sincronize silenciosamente; depois de assumir, entregar,
revisar ou criar uma tarefa/skill, salve e envie silenciosamente. Não ensine Git nem peça comandos.

Explique conceitos com palavras simples, uma ação por vez e checkpoints curtos. Não solicite nem
grave tokens na conversa ou no Git. Não habilite Infinitum nem escrita em sistema externo durante
este laboratório. Ao final, rode o diagnóstico e mostre apenas o que está pronto e qualquer ação
pessoal inevitável.
```

### Prompt 2 — Colaborador

O Dono deve substituir o marcador pelo código antes de entregar este prompt.

```text
Instale o Kit 2 - Implementando sua Esteira de Petições Automatizadas usando esta fonte oficial:
https://github.com/marcuspeterson1/fazedoria-claude-juridico-2

Meu código de entrada é "SEU_CODIGO_ENTRADA".

Leia e audite os arquivos antes de executar qualquer coisa. Faça tudo por mim usando suas ferramentas
internas, sem me mandar abrir Terminal, PowerShell ou Prompt de Comando. Conduza como se eu nunca
tivesse ouvido falar em GitHub: explique com palavras simples, uma ação por vez e checkpoints curtos.

Se eu ainda não tiver conta no GitHub, abra a página oficial de cadastro no navegador e acompanhe o
passo a passo. Eu mesmo preencherei senha, confirmação de e-mail, captcha e autenticação. Depois faça
o login oficial pelo navegador e identifique automaticamente meu nome de usuário, sem mostrar token.

Decodifique o código para descobrir o escritório, o repositório privado e meu papel. Não me pergunte
nome do escritório, função, agente ou pasta técnica. Pergunte somente meu nome. Se meu usuário ainda
não tiver acesso ao repositório privado, mostre-o claramente para que o Dono envie o convite e aguarde
minha confirmação; depois retome nesta mesma conversa, clone o repositório e execute
`entrar-com-codigo` sem pedir novamente dados já respondidos.

Crie automaticamente a pasta local padrão para os casos, instale as skills e ative a sincronização em
segundo plano. Sincronize silenciosamente antes de mostrar a fila e depois de cada alteração. Não me
ensine Git nem peça comandos. Nunca solicite nem grave tokens na conversa ou no Git. Não habilite
Infinitum nem escrita em sistema externo durante este laboratório. Ao final, rode o diagnóstico e
mostre apenas o que está pronto e qualquer ação pessoal inevitável.
```

## Como funciona o código de entrada

O código não é senha e não contém credencial. Ele carrega a identidade do escritório, o endereço do
repositório privado e o papel Controller ou Advogado, com verificação contra alteração. O GitHub continua exigindo
login pessoal e convite prévio para proteger os dados do escritório. Depois disso, o colaborador não
digita novamente o nome do escritório nem escolhe seu papel.

## Fluxo operacional

O primeiro computador executa `iniciar-escritorio`; o Dono usa `gerar-codigo --papel controller` ou
`gerar-codigo --papel advogado`; os demais usam `entrar-com-codigo`. O comando
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
