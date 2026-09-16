# Guia de início rápido

## Criar seu projeto

Após instalar (`python -m pip install -e .`), rode `tcc-kit init ./meu-tcc` e responda às perguntas. Use “Ainda não definido” para uma decisão que não tomou. A ferramenta não preenche fatos de pesquisa. O destino deve ser uma pasta nova: arquivos existentes não são sobrescritos.

## Usar com um assistente de IA

`tcc-kit prompt --project ./meu-tcc --section introducao` imprime um roteiro contextualizado. Ele não envia nada automaticamente. Se copiar material para um serviço externo, confira as regras de privacidade da instituição e remova dados confidenciais.

## Registrar uma fonte

`tcc-kit source add DOI --project ./meu-tcc` consulta a agência registradora e metadados do registro DOI. Confirme autores, título, ano e editora/periódico na fonte original. Metadados incompletos ficam explícitos. Sem internet, a consulta não funciona; os arquivos do projeto continuam locais.

## Conferir e exportar

`tcc-kit check ./meu-tcc` confere a sintaxe suportada e as chaves do registro local. `tcc-kit format ./meu-tcc --format docx` gera `TCC_FORMATADO.docx` e um relatório `.report.json`. Para substituir uma saída existente, acrescente `--force`.

O DOCX é editável. O perfil inicial é `preview`; não use o resultado como prova de conformidade. PDF automático não está disponível na versão alfa.

## Automação com JSON

Crie um JSON UTF-8 com `topic`, `course`, `institution`, `work_type`, `problem`, `objectives` e `method`; execute `tcc-kit init ./meu-tcc --answers-json respostas.json`. Todos os valores devem ser textos. Chaves desconhecidas são recusadas.
