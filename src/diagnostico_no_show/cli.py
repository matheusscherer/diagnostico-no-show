"""Interface de linha de comando."""

from __future__ import annotations

import argparse
from pathlib import Path

from diagnostico_no_show.analyzer import run_diagnosis
from diagnostico_no_show.config import (
    DEFAULT_AGENDAMENTOS_PATH,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_PROFISSIONAIS_PATH,
)
from diagnostico_no_show.models import NoShowPolicy
from diagnostico_no_show.report import build_markdown_report, save_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="diagnostico-no-show",
        description="Diagnóstico de no-show: receita perdida + ociosidade de agenda.",
    )
    parser.add_argument(
        "--agendamentos",
        type=Path,
        default=DEFAULT_AGENDAMENTOS_PATH,
        help="Caminho do CSV de agendamentos",
    )
    parser.add_argument(
        "--profissionais",
        type=Path,
        default=DEFAULT_PROFISSIONAIS_PATH,
        help="Caminho do CSV de profissionais (opcional)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Diretório de saída dos relatórios",
    )
    parser.add_argument(
        "--recovery-rate",
        type=float,
        default=0.25,
        help="Taxa conservadora de recuperação potencial (default: 0.25)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Apenas imprime o relatório no terminal, sem salvar arquivos",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    policy = NoShowPolicy(recovery_rate=args.recovery_rate)

    result = run_diagnosis(
        agendamentos_path=args.agendamentos,
        profissionais_path=args.profissionais,
        policy=policy,
    )

    report = build_markdown_report(result)
    print(report)

    if not args.no_save:
        paths = save_reports(result, args.output)
        print("\nArquivos gerados:")
        print(f"  - {paths['markdown']}")
        print(f"  - {paths['excel']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
