# Kit 2 — Método Euro

Um núcleo único para Controller e Advogado, Claude Code e Codex, um ou vários colaboradores. O
O repositório público deste Kit é apenas o molde, sem dados. Durante a instalação, o Claude cria um
novo repositório **privado** para o escritório. Esse repositório privado é a fonte canônica; cada
pessoa usa sua conta pessoal do GitHub e
um clone próprio. O núcleo funciona sem software jurídico:

`Sync/congelado (leitura) → fila GitHub → Controller → Advogado → revisão → proposta → skill`

O Infinitum é opcional. O modo inicial é sempre `sandbox` e bloqueia efeitos externos.

## Instalação guiada por um prompt

Abra Claude Code na pasta permanente `Claude` e envie o texto abaixo. O aluno não precisa abrir
Terminal ou PowerShell.

```text
Instale o Kit 2 do Método Euro a partir do repositório público informado pelo professor. Leia e
audite os arquivos antes de executar qualquer coisa. Faça tudo por mim usando suas ferramentas
internas, sem me mandar abrir terminal. Explique que o repositório público é apenas um molde. Crie
para meu escritório um novo repositório privado, copie o Kit para ele e confirme pela configuração
do GitHub que está privado antes de cadastrar qualquer caso ou tarefa. Peça apenas o login oficial
do GitHub no navegador se for inevitável. Cada pessoa usa sua própria conta e seu próprio clone.

Execute o assistente de configuração em modo sandbox. Explique cada conceito com palavras simples e
uma analogia antes de agir. Pergunte meu nome, escritório, papel (controller ou advogado), agente
(Claude Code ou Codex) e o caminho local autorizado dos casos. Faça uma pergunta por vez e mostre
um checkpoint simples depois de cada etapa.
Não solicite nem grave tokens na conversa ou no Git. Não habilite Infinitum nem escrita em sistema
externo. Configure com a confirmação de repositório privado. Ao final, rode o diagnóstico e mostre
os checkpoints em linguagem simples.
```

## Fluxo operacional

O assistente executa `python3 euro.py configurar`. Depois:

- `python3 euro.py instalar-skills` liga a fonte canônica aos diretórios reconhecidos por Claude Code
  e Codex, preservando qualquer instalação preexistente.
- `python3 euro.py preparar-auto-sync` cria os arquivos locais para sincronização conservadora a cada
  dez minutos. O Claude instala/ativa o agendamento nativo do sistema e comprova uma execução.

1. Controller: `criar-tarefa`, confere e sincroniza.
2. Advogado: `listar`, `assumir ID`, `contexto ID`, produz arquivo e `entregar ID ARQUIVO`.
3. Controller: `revisar ID aprovada|ajustes|reprovada --feedback ...`.
4. Se houver aprendizado reutilizável: `propor-skill`; após revisão, `promover-skill`.

Use `python3 euro.py --help` para os argumentos. `sincronizar` faz pull com rebase e push somente se
o clone tiver remote; em conflito, para e preserva o estado para conciliação humana.

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
