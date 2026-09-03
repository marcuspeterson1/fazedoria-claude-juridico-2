---
name: resumo-do-processo
description: "Gera resumo jurídico padronizado a partir dos autos obtidos no Sync: Situação, Partes, Linha do tempo essencial, Pontos de atenção e Pendências. Use sempre que o usuário pedir resumo do processo ou resumo do caso."
metadata:
  category: Processual
---

# Resumo do processo — formato

Escreva de advogado para advogado: seja objetivo, telegráfico, sem didatismo, sem elogio e sem
repetir o título. Não use fórmulas vazias como “conforme se depreende dos autos”. Não invente fatos,
datas, partes ou pendências que não estejam no contexto entregue pelo Sync.

Entregue Markdown com exatamente estas seções, nesta ordem:

## Situação

Uma frase com o estado ou resultado atual do processo: sentença, acordo, instrução, arquivamento ou
ato aguardado. Havendo resultado, informe se foi procedente, improcedente ou parcial e quem ganhou o
quê. Não coloque histórico nesta seção.

## Partes

Uma linha por parte: nome, polo — autor, réu ou terceiro — e, quando constar, advogado. Marque quem é
o cliente do escritório. Se isso não estiver identificado nos autos, declare a lacuna.

## Linha do tempo essencial

Liste apenas os marcos que explicam como o processo chegou ao estado atual: distribuição, citação,
contestação, decisões, perícia, sentença, recursos e trânsito. Use uma linha por marco no formato
`DD/MM/AAAA — fato`, do mais antigo ao mais recente. Corte juntadas, conclusões, remessas e publicações
repetidas que não mudem o caso. Na maioria dos processos, use entre 5 e 15 linhas.

## Pontos de atenção

Registre apenas o que altera estratégia ou risco: decisão desfavorável, multa, penhora, tese acolhida
ou rejeitada, valor fixado, lacuna relevante ou paralisação prolongada. Se não houver, escreva
“nada relevante”.

## Pendências

Informe o que continua em aberto e depende de alguém: prazo, ato, documento ou decisão aguardada.
Se não houver, escreva “nenhuma pendência identificada”.
