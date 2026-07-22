# Gerenciador de Saves do Stardew Valley

[English](README.md) | [简体中文](README.zh.md) | [Español](README.es.md) | [日本語](README.jp.md)

Aplicativo de desktop para Windows que permite consultar e editar com segurança informações selecionadas de saves do Stardew Valley. Ele utiliza o local padrão de saves do Windows e o executável de lançamento não requer instalação do Python.

## Download

Baixe `StardewValleySaveManager.exe` no [último GitHub Release](https://github.com/fyihang/StardewValleyTool/releases). Não é necessário instalar Python para usar o executável de lançamento.

## O que pode ser editado

- Nome do fazendeiro
- Nome da fazenda
- Coisa favorita
- Nome dos animais existentes, inclusive o cavalo quando houver um
- Nome e coisa favorita dos trabalhadores agrícolas existentes, selecionados em uma lista (o nome da fazenda continua sendo uma configuração exclusiva do proprietário)

A interface está disponível em inglês, chinês simplificado, português, espanhol e japonês. Os tipos de animais são traduzidos para o idioma escolhido; tipos desconhecidos de animais adicionados por mods continuam visíveis com o valor original do jogo.

## Proteção dos saves

Ao iniciar, o aplicativo procura o diretório padrão do Windows:

```text
%appdata%\StardewValley\Saves
```

Use **Escolher diretório de saves** para selecionar outra raiz de saves somente durante a sessão atual. Essa escolha não é gravada; na próxima abertura, o aplicativo volta a usar o diretório padrão.

Um save só é reconhecido quando sua pasta contém `SaveGameInfo` e o arquivo principal com o mesmo nome da pasta. As informações do proprietário presentes nos dois arquivos são atualizadas em ambos. Trabalhadores agrícolas e animais são editados apenas no arquivo principal, onde esses registros são armazenados.

Antes de gravar, o aplicativo copia os dois arquivos para `.svt-backups/<carimbo de data e hora UTC>/` dentro da pasta do save. Ele valida os XML temporários antes da substituição e confere o resultado salvo depois. Se ocorrer um erro durante a operação, os dois arquivos originais são restaurados a partir do backup.

## Como usar

1. Feche completamente o Stardew Valley.
2. Inicie `StardewValleySaveManager.exe`.
3. Selecione um save na lista à esquerda.
4. Edite os campos do proprietário; se houver trabalhadores agrícolas, selecione um deles na lista; dê dois cliques no nome de um animal para renomeá-lo.
5. Selecione **Salvar alterações** e confirme que o jogo está fechado.

No primeiro uso, faça uma cópia independente de uma pasta de save e teste as alterações nela. Mantenha a pasta `.svt-backups` gerada até verificar o save editado dentro do jogo.

## Código-fonte

Para executar a partir do código-fonte, instale Python 3.11 ou superior e execute, na raiz do repositório:

```powershell
$env:PYTHONPATH = "src"
python src\__main__.py
```

## Licença

Distribuído sob a [licença MIT](LICENSE).
