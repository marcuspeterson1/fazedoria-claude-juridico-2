---
name: configurar-kit2
description: Configura uma bancada segura do Kit 2 para Dono, Controller ou Advogado.
---

# Configurar Kit 2

Leia `README.md` e audite o repositório público, que é apenas o molde. Há dois prompts: o Dono instala
primeiro e entrega ao colaborador o Prompt 2 já preenchido com o código. O primeiro instalador cria o repositório privado e
usa `iniciar-escritorio`; ele fica registrado como Dono/Administrador e escolhe se também será
Controller. Somente o Dono gera códigos específicos para Controller ou Advogado. Quem recebeu código não
informa novamente escritório, papel, agente ou caminho: decodifique, clone o privado e use
`entrar-com-codigo`, pedindo somente o nome pessoal. Código não substitui o convite pessoal exigido
pelo GitHub. Se o convite ainda faltar, identifique automaticamente o usuário GitHub, mostre-o para
o Dono convidar e retome a mesma instalação assim que o acesso for liberado.
Conduza como tutor de iniciante absoluto: uma pergunta e uma ação por vez, analogias simples,
explicação do motivo, checkpoint visual e correção paciente dos erros, sem infantilizar a pessoa.
Instale silenciosamente Python 3 oficial se faltar; não ofereça escolhas técnicas ao iniciante.
Se não existir conta GitHub, abra a página oficial de criação no navegador e acompanhe a pessoa passo
a passo; ela própria digita senha, confirmação de e-mail e autenticação. Depois autentique o GitHub
CLI pelo navegador e identifique a conta ativa sem exibir tokens. Nunca peça token na conversa. Crie uma pasta padrão para casos,
execute `instalar-skills` e `preparar-auto-sync`; instale o arquivo de
agendamento gerado pelo mecanismo nativo do sistema, sem editar seu intervalo de dez minutos. Termine
com `diagnosticar`, comprove uma sincronização e traduza o resultado em checkpoints simples.

O Sync é obrigatório como fonte de autos em operação. Em cada computador autorizado, abra a entrada
segura nativa e execute `configurar-sync` sem receber a chave na conversa, argumento ou Git; valide
com `testar-sync`. O código de entrada nunca transporta essa credencial. Quando o Advogado assumir
tarefa, execute `contexto`: ele materializa localmente a cronologia e os Markdowns em pasta ignorada
pelo Git.
