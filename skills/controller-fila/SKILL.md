---
name: controller-fila
description: Cria, distribui e acompanha tarefas jurídicas na fila GitHub do Método Euro.
---

# Controller da fila

Confirme o papel Controller e o modo MVP. Leia o Sync sem alterar o processo. Registre CNJ,
providência sugerida, responsável e referência da entrada com `criar-tarefa`. Não calcule prazo fatal
nem transforme sugestão em decisão. Sincronize e confirme que o arquivo da tarefa foi versionado.

Mesmo que a máquina tenha outra Esteira ou integração antiga, não use nenhuma ação de escrita no
Sync: não marque intimação como tratada, não altere monitoramento e não atualize cache operacional de
outro sistema. Apresentar intimações é somente ler. Se a sincronização da fila falhar, não declare que
ela está vazia; informe que o remoto não pôde ser confirmado.
