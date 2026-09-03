---
name: atualizar-kit
description: Atualiza uma instalação existente do Kit 2 a partir da fonte pública oficial, aplicando somente novidades e preservando dados e personalizações do escritório.
---

# Atualizar Kit 2

Use quando o professor informar que há uma versão nova ou quando o usuário repetir um dos prompts de
instalação em um Kit já configurado. Antes de agir, leia `versao-kit.json` e
`manifesto-arquivos.json` na fonte pública oficial e na cópia privada do escritório.

## Regra central

Instalação existente não é reinstalação. Não recrie repositório, organização, Dono, códigos, clone,
fila, entregas, propostas, credenciais, caminhos locais ou agendamentos. Não peça novamente dados já
registrados. Compare versões e hashes e aplique apenas arquivos oficiais novos ou alterados.

Os caminhos listados como `preservar_sempre` no manifesto pertencem ao escritório. Nunca os
substitua pela cópia pública. Para `metodo-euro.json`, preserve identidade, organização e configuração
documental preenchida; acrescente somente chaves novas ausentes. Skills criadas pelo escritório não
são apagadas. Se uma skill oficial tiver sido personalizada, preserve as duas versões e peça ao Dono
para conciliar; não escolha silenciosamente.

Antes de aplicar, crie um ponto de restauração Git. Depois, instale novamente os links de skills de
forma idempotente, rode os testes e `diagnosticar`, registre a versão instalada na configuração local
e sincronize o repositório privado. Mostre em checkpoint: versão anterior e nova, arquivos incluídos,
alterados, preservados e conflitos. Se já estiver atualizado, não modifique nada.
