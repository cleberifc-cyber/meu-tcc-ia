# meu-tcc-ia

Repositório de apoio à elaboração de um Trabalho de Conclusão de Curso (TCC) com assistência de IA. A autoria, a verificação das fontes, a adequação às regras da instituição e a decisão sobre cada trecho permanecem sob responsabilidade do estudante e de seu orientador.

## Fluxo sugerido

1. Defina tema, problema, objetivos e escopo com o orientador.
2. Registre fontes rastreáveis em `src/referencias.bib`; não aceite referências que não possam ser localizadas.
3. Use os roteiros em `prompts/` apenas como apoio, fornecendo fontes e limites explícitos.
4. Revise cada afirmação, citação, dado e paráfrase contra a fonte original.
5. Mantenha os textos aprovados em `src/` e confira as normas vigentes e o manual da instituição antes da entrega.
6. A GitHub Action tenta compilar `src/tcc.md` para PDF quando esse arquivo existir; nenhum PDF é gerado a partir de conteúdo fictício.

## Estrutura

- `prompts/`: roteiros de trabalho por etapa.
- `templates/`: guia inicial e espaço para modelos autorizados.
- `src/`: manuscrito e referências do estudante.
- `.github/workflows/`: compilação automatizada do PDF.

## Segurança e integridade acadêmica

Nunca salve tokens, senhas, dados pessoais desnecessários ou material sem autorização neste repositório. Confirme as políticas da instituição sobre uso de IA, autoria, confidencialidade e divulgação. As normas ABNT e os regulamentos institucionais podem ser atualizados; consulte as versões aplicáveis e as orientações de sua instituição.
