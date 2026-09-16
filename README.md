# TCC Kit — pesquisa, fontes e formatação em um fluxo local

[English overview](README.en.md)

![TCC Kit — pesquisa, fontes e formatação](.github/social-preview.png)

Ferramentas abertas, em português, para organizar um Trabalho de Conclusão de Curso, registrar metadados de fontes por DOI, conferir citações e gerar um DOCX editável. O projeto é alfa (`0.1.0a1`): funciona sem conta de IA e mantém o manuscrito no seu computador.

> O perfil incluído é `preview`, não certificação de conformidade ABNT. Ele não consulta automaticamente o texto vigente das normas. Confira o manual da sua instituição e as edições oficiais antes de entregar o trabalho.

## Comece (Windows)

Instale Python 3.11 ou superior e Git. No PowerShell:

```powershell
git clone https://github.com/cleberifc-cyber/meu-tcc-ia.git
cd meu-tcc-ia
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
tcc-kit init .\meu-tcc
tcc-kit prompt --project .\meu-tcc --section introducao
tcc-kit check .\meu-tcc
tcc-kit format .\meu-tcc --format docx
```

Se ainda não tem uma fonte real, não use DOI de exemplo como se fosse referência. `source add` consulta uma agência DOI e metadados públicos no Crossref ou DataCite. Confira cada registro no site do DOI. A busca envia apenas o DOI, nunca o manuscrito.

## macOS e Linux

```sh
git clone https://github.com/cleberifc-cyber/meu-tcc-ia.git
cd meu-tcc-ia
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
tcc-kit init ./meu-tcc
tcc-kit check ./meu-tcc
tcc-kit format ./meu-tcc --format docx
```

Veja o [guia de início rápido](docs/quickstart.md) para modo interativo, respostas JSON e solução de problemas.

## Teste rápido sem IA

Depois de instalar, gere um projeto demonstrativo, peça um prompt e exporte o esqueleto:

```sh
tcc-kit init ./meu-tcc-demo --answers-json ./examples/demo/answers.json
tcc-kit prompt --project ./meu-tcc-demo --section introducao
tcc-kit check ./meu-tcc-demo
tcc-kit format ./meu-tcc-demo --format docx
```

No PowerShell, troque `./` por `.\` se preferir. O exemplo é fictício, não traz fontes inventadas e não produz um TCC pronto. A pasta `meu-tcc-demo/` fica ignorada pelo Git.

## O que a versão alfa faz

- Cria projeto com questionário, manuscrito Markdown, registro JSON de fontes e prompts por etapa.
- Gera instruções contextualizadas sem chamar uma IA; copie-as para o assistente que preferir.
- Consulta metadados DOI em APIs públicas Crossref/DataCite e registra proveniência local por campo.
- Aponta citações `[@chave]` sem registro e metadados bibliográficos faltantes.
- Renderiza DOCX com página de rosto, títulos, parágrafos, listas, tabelas e imagens locais no subconjunto documentado de Markdown.
- Emite relatório JSON com perfil, avisos e hashes dos arquivos de entrada.

## Formatação: transparência primeiro

O perfil `abnt-br-preview` produz uma apresentação inicial configurável; não afirma ser implementação integral ou atualizada das NBR. Estruturas avançadas de Markdown, citações, tipos de referência, paginação e regras institucionais ainda não estão todas cobertas. A exportação lista avisos e mantém os arquivos fonte sem alteração. PDF automático ainda não está incluído nesta versão.

O registro DOI usa metadados depositados por terceiros; pode haver lacunas ou erros. A ferramenta não baixa artigos completos, não inventa referências e não valida a qualidade científica de uma fonte. Consulte [estado e limites do perfil](docs/abnt/profile-status.md).

## Privacidade e integridade acadêmica

O padrão é local, sem provedor de IA, telemetria ou serviço hospedado. A única operação de rede implementada é a consulta DOI solicitada pelo usuário, enviando o identificador DOI. Leia [privacidade e dados](docs/privacy.md). Prompts não substituem orientação, leitura das fontes, autoria ou políticas da instituição.

## Desenvolvimento

```sh
python -m pip install -e ".[test]"
python -m pytest -q
python -m build
```

Contribuições são bem-vindas: consulte [CONTRIBUTING.md](CONTRIBUTING.md), [CHANGELOG.md](CHANGELOG.md) e [ROADMAP.md](ROADMAP.md). Não há badge de CI até existir uma execução real bem-sucedida.

## Apoie o projeto

Contribuições de código, documentação e relatos de problemas são muito bem-vindas. Se preferir apoiar financeiramente, há um endereço opcional para USDT na rede TRON (TRC20):

```text
TQCMKPwkQwGCz31se4X4BqbzzFfmj7XK8D
```

Envie somente USDT pela rede TRON/TRC20. Confirme cuidadosamente a rede, o ativo e o endereço na sua carteira antes de enviar; transferências em criptoativos podem ser irreversíveis, e taxas de rede podem ser aplicadas. O apoio é voluntário, sem benefícios ou garantia de resposta/resultado. Nunca compartilhe sua frase-semente ou chave privada.

## Licença

Código e materiais originais sob MIT. Normas ABNT, dados de provedores e conteúdo de terceiros não estão incluídos e conservam seus direitos e termos; veja [THIRD_PARTY.md](THIRD_PARTY.md).
