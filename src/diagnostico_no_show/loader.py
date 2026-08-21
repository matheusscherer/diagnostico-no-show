"""Carregamento e validação dos dados de entrada."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from diagnostico_no_show.config import VALID_STATUS

REQUIRED_AGENDAMENTO_COLS = [
    "id",
    "data",
    "hora",
    "profissional",
    "servico",
    "ticket",
    "status",
    "canal",
    "confirmado",
]

REQUIRED_PROFISSIONAL_COLS = ["profissional", "custo_hora", "capacidade_dia"]


def _normalize_text(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower()


def load_agendamentos(path: Path) -> pd.DataFrame:
    """Lê e valida o arquivo de agendamentos."""
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de agendamentos não encontrado: {path}")

    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_AGENDAMENTO_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes em agendamentos: {missing}")

    df = df.copy()
    df["id"] = df["id"].astype(str).str.strip()
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    if df["data"].isna().any():
        raise ValueError("Existem datas inválidas em agendamentos")

    df["hora"] = df["hora"].astype(str).str.strip()
    df["profissional"] = df["profissional"].astype(str).str.strip()
    df["servico"] = df["servico"].astype(str).str.strip()
    df["canal"] = df["canal"].astype(str).str.strip()

    df["ticket"] = pd.to_numeric(df["ticket"], errors="coerce")
    if df["ticket"].isna().any() or (df["ticket"] < 0).any():
        raise ValueError("ticket deve ser numérico e >= 0")

    df["status"] = _normalize_text(df["status"])
    invalid_status = set(df["status"].unique()) - VALID_STATUS
    if invalid_status:
        raise ValueError(
            f"status inválidos: {sorted(invalid_status)}. "
            f"Use apenas: {sorted(VALID_STATUS)}"
        )

    df["confirmado"] = _normalize_text(df["confirmado"])
    df["confirmado"] = df["confirmado"].map(
        {"sim": True, "nao": False, "não": False, "yes": True, "no": False}
    )
    if df["confirmado"].isna().any():
        raise ValueError("confirmado deve ser sim/nao")

    # Faixa horária para ranking (ex.: 14:30 -> 14h)
    df["faixa_hora"] = df["hora"].str.slice(0, 2).str.zfill(2) + "h"

    # Dia da semana
    weekdays = {
        0: "segunda",
        1: "terca",
        2: "quarta",
        3: "quinta",
        4: "sexta",
        5: "sabado",
        6: "domingo",
    }
    df["dia_semana"] = df["data"].dt.dayofweek.map(weekdays)

    return df.reset_index(drop=True)


def load_profissionais(path: Path | None) -> pd.DataFrame | None:
    """Lê profissionais (opcional). Retorna None se arquivo não existir."""
    if path is None or not path.exists():
        return None

    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_PROFISSIONAL_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes em profissionais: {missing}")

    df = df.copy()
    df["profissional"] = df["profissional"].astype(str).str.strip()
    df["custo_hora"] = pd.to_numeric(df["custo_hora"], errors="coerce")
    df["capacidade_dia"] = pd.to_numeric(df["capacidade_dia"], errors="coerce")

    if df["custo_hora"].isna().any() or (df["custo_hora"] < 0).any():
        raise ValueError("custo_hora deve ser numérico e >= 0")
    if df["capacidade_dia"].isna().any() or (df["capacidade_dia"] <= 0).any():
        raise ValueError("capacidade_dia deve ser numérico e > 0")

    return df.reset_index(drop=True)
