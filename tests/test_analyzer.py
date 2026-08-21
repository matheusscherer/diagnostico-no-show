"""Testes de integração do analyzer."""

from __future__ import annotations

from pathlib import Path

from diagnostico_no_show.analyzer import run_diagnosis
from diagnostico_no_show.report import build_markdown_report


def test_run_diagnosis_end_to_end(data_dir: Path) -> None:
    result = run_diagnosis(
        agendamentos_path=data_dir / "agendamentos.csv",
        profissionais_path=data_dir / "profissionais.csv",
    )
    assert result.summary["total_no_show"] == 2
    assert result.receita_perdida == 80.0
    assert not result.by_profissional.empty

    md = build_markdown_report(result)
    assert "Receita perdida" in md
    assert "Diagnóstico de No-Show" in md
