"""Testes das métricas."""

from __future__ import annotations

import pandas as pd

from diagnostico_no_show.metrics import compute_summary, rank_by
from diagnostico_no_show.models import NoShowPolicy


def test_compute_summary_receita(
    sample_agendamentos: pd.DataFrame,
    sample_profissionais: pd.DataFrame,
    policy: NoShowPolicy,
) -> None:
    summary = compute_summary(sample_agendamentos, sample_profissionais, policy)
    # 2 no-shows: 30 + 50 = 80
    assert summary["receita_perdida_rs"] == 80.0
    assert summary["total_no_show"] == 2
    assert summary["taxa_no_show_pct"] == 50.0  # 2 de 4
    # ociosidade: Ana 40 + Bruno 50 = 90
    assert summary["custo_ociosidade_rs"] == 90.0
    assert summary["potencial_recuperacao_rs"] == 20.0  # 25% de 80


def test_rank_by_profissional(
    sample_agendamentos: pd.DataFrame,
    sample_profissionais: pd.DataFrame,
) -> None:
    ranking = rank_by(sample_agendamentos, "profissional", sample_profissionais)
    assert len(ranking) == 2
    assert ranking.iloc[0]["receita_perdida_rs"] >= ranking.iloc[1]["receita_perdida_rs"]
