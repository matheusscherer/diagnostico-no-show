"""Testes do loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from diagnostico_no_show.loader import load_agendamentos, load_profissionais


def test_load_agendamentos_ok(data_dir: Path) -> None:
    df = load_agendamentos(data_dir / "agendamentos.csv")
    assert len(df) == 4
    assert "faixa_hora" in df.columns
    assert set(df["status"].unique()) <= {"compareceu", "no_show", "cancelado", "remarcado"}


def test_load_profissionais_ok(data_dir: Path) -> None:
    df = load_profissionais(data_dir / "profissionais.csv")
    assert df is not None
    assert len(df) == 2
    assert "custo_hora" in df.columns


def test_load_agendamentos_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_agendamentos(tmp_path / "nao_existe.csv")
