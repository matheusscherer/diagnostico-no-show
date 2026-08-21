"""Fixtures compartilhadas."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from diagnostico_no_show.models import NoShowPolicy


@pytest.fixture
def sample_agendamentos() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": "A1",
                "data": pd.Timestamp("2026-08-01"),
                "hora": "10:00",
                "profissional": "Ana",
                "servico": "Corte",
                "ticket": 50.0,
                "status": "compareceu",
                "canal": "WhatsApp",
                "confirmado": True,
                "faixa_hora": "10h",
                "dia_semana": "sexta",
            },
            {
                "id": "A2",
                "data": pd.Timestamp("2026-08-01"),
                "hora": "11:00",
                "profissional": "Ana",
                "servico": "Barba",
                "ticket": 30.0,
                "status": "no_show",
                "canal": "Instagram",
                "confirmado": False,
                "faixa_hora": "11h",
                "dia_semana": "sexta",
            },
            {
                "id": "A3",
                "data": pd.Timestamp("2026-08-01"),
                "hora": "14:00",
                "profissional": "Bruno",
                "servico": "Corte",
                "ticket": 50.0,
                "status": "no_show",
                "canal": "WhatsApp",
                "confirmado": False,
                "faixa_hora": "14h",
                "dia_semana": "sexta",
            },
            {
                "id": "A4",
                "data": pd.Timestamp("2026-08-01"),
                "hora": "15:00",
                "profissional": "Bruno",
                "servico": "Coloração",
                "ticket": 100.0,
                "status": "compareceu",
                "canal": "Telefone",
                "confirmado": True,
                "faixa_hora": "15h",
                "dia_semana": "sexta",
            },
        ]
    )


@pytest.fixture
def sample_profissionais() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"profissional": "Ana", "custo_hora": 40.0, "capacidade_dia": 8},
            {"profissional": "Bruno", "custo_hora": 50.0, "capacidade_dia": 8},
        ]
    )


@pytest.fixture
def policy() -> NoShowPolicy:
    return NoShowPolicy(recovery_rate=0.25)


@pytest.fixture
def data_dir(tmp_path: Path, sample_agendamentos: pd.DataFrame, sample_profissionais: pd.DataFrame) -> Path:
    raw = tmp_path / "raw"
    raw.mkdir()
    # Exporta no formato de entrada (confirmado como sim/nao)
    age = sample_agendamentos.copy()
    age["data"] = age["data"].dt.strftime("%Y-%m-%d")
    age["confirmado"] = age["confirmado"].map({True: "sim", False: "nao"})
    age = age.drop(columns=["faixa_hora", "dia_semana"])
    age.to_csv(raw / "agendamentos.csv", index=False)
    sample_profissionais.to_csv(raw / "profissionais.csv", index=False)
    return raw
