"""Interface de linha de comando do TCC Kit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tcc_kit.project import collect_answers, create_project
from tcc_kit.prompts import build_prompt
from tcc_kit.validation import validate_project
from tcc_kit.formatting.docx import render_docx
from tcc_kit.formatting.profile import RuleProfile
from tcc_kit.sources.service import add_doi


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tcc-kit",
        description="Planeje, documente fontes e prepare seu TCC com rastreabilidade.",
    )
    commands = parser.add_subparsers(dest="command")
    init = commands.add_parser("init", help="criar um projeto de TCC guiado")
    init.add_argument("destination", type=Path, help="pasta nova do projeto")
    init.add_argument("--answers-json", type=Path, help="arquivo JSON de respostas (automação)")
    prompt = commands.add_parser("prompt", help="gerar orientação para uma etapa do TCC")
    prompt.add_argument("--project", type=Path, required=True)
    prompt.add_argument("--section", choices=("introducao", "referencial", "metodologia"), required=True)
    source = commands.add_parser("source", help="buscar e registrar metadados de uma fonte")
    source.add_argument("action", nargs="?", default="add")
    source.add_argument("doi", nargs="?")
    source.add_argument("--project", type=Path)
    check = commands.add_parser("check", help="validar citações e referências do projeto")
    check.add_argument("project", type=Path)
    format_command = commands.add_parser("format", help="exportar o manuscrito para DOCX ou PDF")
    format_command.add_argument("project", type=Path)
    format_command.add_argument("--output", type=Path)
    format_command.add_argument("--profile", type=Path)
    format_command.add_argument("--format", choices=("docx",), default="docx")
    format_command.add_argument("--force", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.command == "init":
        try:
            if args.answers_json:
                answers = json.loads(args.answers_json.read_text(encoding="utf-8"))
                if not isinstance(answers, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in answers.items()):
                    raise ValueError("O JSON deve ser um objeto com valores de texto.")
            else:
                answers = collect_answers(input, print)
            created = create_project(args.destination, answers)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        print(f"Projeto criado em: {args.destination}")
        for path in created:
            print(f"  {path.name}")
        return 0
    if args.command == "prompt":
        try:
            print(build_prompt(args.project, args.section))
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        return 0
    if args.command == "check":
        try:
            diagnostics = validate_project(args.project)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        for item in diagnostics:
            where = f"{item.path}:{item.line}" if item.line else item.path
            print(f"{item.severity.upper()} [{item.code}] {where}: {item.message}")
        if not diagnostics:
            print("Projeto validado: nenhuma citação não resolvida ou erro estrutural detectado.")
        return 1 if any(item.severity == "error" for item in diagnostics) else 0
    if args.command == "format":
        try:
            profile = RuleProfile.load(args.profile) if args.profile else RuleProfile.bundled()
            output = args.output or (args.project / "TCC_FORMATADO.docx")
            report = render_docx(args.project, output, profile, force=args.force)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        print(f"DOCX criado: {report.output}")
        print(f"Perfil: {report.profile_id} ({report.profile_status})")
        print(f"Relatório: {output.with_suffix('.report.json')}")
        for warning in report.warnings:
            print(f"AVISO: {warning}")
        return 0
    if args.command == "source":
        if args.action != "add" or not args.doi or not args.project:
            parser.error("Use: tcc-kit source add DOI --project PASTA")
        try:
            record = add_doi(args.project, args.doi)
        except (OSError, ValueError, LookupError, ConnectionError) as exc:
            parser.error(str(exc))
        print(f"Referência candidata: [@{record.key}]")
        print(f"Tipo: {record.item_type}; DOI: {record.fields.get('doi', '')}")
        for field, value in record.fields.items():
            print(f"{field}: {value}")
        missing = [field for field in ("author", "title") if not record.fields.get(field)]
        if missing:
            print("CONFIRA: metadados ausentes: " + ", ".join(missing))
        print("Confira os metadados na página do DOI antes de citar.")
        return 0
    if args.command in {"check", "format"}:
        parser.error(f"O comando '{args.command}' ainda não está disponível nesta versão.")
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
