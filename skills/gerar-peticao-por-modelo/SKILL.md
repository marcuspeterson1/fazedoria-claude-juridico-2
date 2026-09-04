---
name: gerar-peticao-por-modelo
description: Gera uma petição a partir de uma cópia de modelo aprovado do escritório, preservando identidade visual, estrutura validada e rastreabilidade.
---

# Gerar petição por modelo

Nunca comece uma petição em documento vazio. Antes de redigir, leia `producao_documental` em
`metodo-euro.json` e localize um modelo aprovado adequado, esteja ele no Google Drive, OneDrive,
disco local, rede ou outro armazenamento autorizado. Use os caminhos locais apenas a partir da
configuração local ignorada pelo Git.

Se nenhum modelo tiver sido fornecido ou localizado, pare a redação e peça ao usuário que indique ou
envie um. Explique em linguagem simples: o modelo é a forma que preserva o “jeito do escritório” —
logomarca, timbre, cabeçalho, rodapé, estilos, margens e estrutura jurídica já validada. Não substitua
essa decisão criando um documento em branco.

## Fluxo obrigatório

1. Confirme qual peça será produzida e selecione o modelo aprovado mais próximo.
2. Faça uma cópia do arquivo original no destino definido pelo escritório. Nunca edite o modelo-mãe.
3. Aplique o padrão de nome do escritório à cópia.
4. Preserve logomarca, timbre, cabeçalho, rodapé, estilos, margens, numeração e demais elementos visuais.
   Para Google Docs, faça uma cópia nativa antes de editar. Para DOCX, preserve a estrutura do original
   e confira cabeçalho, rodapé, imagens, estilos e numeração depois da edição. Se a ferramenta disponível
   não preservar esses elementos, pare; não converta o documento para Markdown ou texto puro.
5. Preserve os tópicos-padrão que façam sentido para o caso; remova os inaplicáveis; acrescente tópicos
   somente quando os autos, a estratégia ou uma solicitação expressa exigirem.
6. Preencha apenas fatos e variáveis comprovados nos autos do Sync. Sinalize lacunas; não invente.
7. Antes de entregar, confira visualmente a cópia e informe: modelo utilizado, destino da cópia,
   tópicos mantidos, removidos e acrescentados.
8. Registre a entrega com `entregar ID ARQUIVO --modelo "IDENTIFICAÇÃO" --copia-destino "DESTINO"`.

O conteúdo pode evoluir; a identidade visual e os tópicos validados não devem ser destruídos por uma
reescrita integral. Revisão humana e protocolo manual permanecem etapas separadas.

Imagens, prints, quadros, citações e marcações inseridos pelo advogado são evidências protegidas. Não
os remova ou substitua antes de compreender e conferir sua fonte. Gere versões numeradas durante a
revisão e nunca mova rascunhos para a lixeira sem autorização expressa. Preferências de estilo devem
ser registradas como princípios (por exemplo, leitura dinâmica e uma ideia por parágrafo), sem inventar
limites numéricos que o usuário não definiu.
