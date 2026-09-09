"""Cálculo das métricas de impacto financeiro do no-show."""

from __future__ import annotations

import pandas as pd

from diagnostico_no_show.config import STATUS_NO_SHOW, STATUS_COMPARECEU
from diagnostico_no_show.models import NoShowPolicy


def _pct(part: float, whole: float) -> float:
    if whole == 0:
        return 0.0
    return round(100.0 * part / whole, 1)


def compute_summary(
    agendamentos: pd.DataFrame,
    profissionais: pd.DataFrame | None,
    policy: NoShowPolicy,
) -> dict:
    """Resumo executivo com os números principais de dinheiro."""
    total = len(agendamentos)
    no_shows = agendamentos[agendamentos["status"] == STATUS_NO_SHOW]
    compareceu = agendamentos[agendamentos["status"] == STATUS_COMPARECEU]

    n_no_show = len(no_shows)
    receita_perdida = float(no_shows["ticket"].sum())
    ticket_medio_no_show = float(no_shows["ticket"].mean()) if n_no_show else 0.0

    # Taxa sobre agendamentos efetivamente "consumidos" (compareceu + no_show)
    base_taxa = len(compareceu) + n_no_show
    taxa_no_show = _pct(n_no_show, base_taxa)

    confirmados = agendamentos[agendamentos["confirmado"]]
    nao_confirmados = agendamentos[~agendamentos["confirmado"]]
    taxa_ns_confirmado = _pct(
        len(confirmados[confirmados["status"] == STATUS_NO_SHOW]),
        len(confirmados[confirmados["status"].isin([STATUS_COMPARECEU, STATUS_NO_SHOW])]),
    )
    taxa_ns_nao_confirmado = _pct(
        len(nao_confirmados[nao_confirmados["status"] == STATUS_NO_SHOW]),
        len(
            nao_confirmados[
                nao_confirmados["status"].isin([STATUS_COMPARECEU, STATUS_NO_SHOW])
            ]
        ),
    )

    # Custo de ociosidade (1 slot ≈ 1 hora, simplificação consciente)
    custo_ociosidade = 0.0
    if profissionais is not None and not profissionais.empty:
        custo_map = profissionais.set_index("profissional")["custo_hora"].to_dict()
        custo_ociosidade = float(
            no_shows["profissional"].map(custo_map).fillna(0.0).sum()
        )

    potencial_recuperacao = round(receita_perdida * policy.recovery_rate, 2)

    periodo_inicio = agendamentos["data"].min().strftime("%Y-%m-%d")
    periodo_fim = agendamentos["data"].max().strftime("%Y-%m-%d")

    return {
        "periodo_inicio": periodo_inicio,
        "periodo_fim": periodo_fim,
        "total_agendamentos": total,
        "total_no_show": n_no_show,
        "total_compareceu": len(compareceu),
        "taxa_no_show_pct": taxa_no_show,
        "receita_perdida_rs": round(receita_perdida, 2),
        "ticket_medio_no_show_rs": round(ticket_medio_no_show, 2),
        "custo_ociosidade_rs": round(custo_ociosidade, 2),
        "impacto_total_rs": round(receita_perdida + custo_ociosidade, 2),
        "potencial_recuperacao_rs": potencial_recuperacao,
        "taxa_ns_confirmado_pct": taxa_ns_confirmado,
        "taxa_ns_nao_confirmado_pct": taxa_ns_nao_confirmado,
        "recovery_rate": policy.recovery_rate,
    }


def rank_by(
    agendamentos: pd.DataFrame,
    group_col: str,
    profissionais: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Ranking de impacto por dimensão (profissional, horário, canal, serviço)."""
    columns = [
        group_col,
        "agendamentos",
        "no_shows",
        "taxa_no_show_pct",
        "receita_perdida_rs",
        "custo_ociosidade_rs",
    ]
    base = agendamentos[
        agendamentos["status"].isin([STATUS_COMPARECEU, STATUS_NO_SHOW])
    ].copy()

    if base.empty:
        return pd.DataFrame(columns=columns)

    ns = base[base["status"] == STATUS_NO_SHOW]
    receita = (
        ns.groupby(group_col)["ticket"]
        .sum()
        .rename("receita_perdida_rs")
        .reset_index()
    )
    counts = (
        base.groupby(group_col)
        .agg(
            agendamentos=("id", "count"),
            no_shows=("status", lambda s: int((s == STATUS_NO_SHOW).sum())),
        )
        .reset_index()
    )
    result = counts.merge(receita, on=group_col, how="left")
    result["receita_perdida_rs"] = result["receita_perdida_rs"].fillna(0.0)
    result["taxa_no_show_pct"] = result.apply(
        lambda r: _pct(r["no_shows"], r["agendamentos"]), axis=1
    )

    if profissionais is not None and not profissionais.empty and group_col == "profissional":
        custo_map = profissionais.set_index("profissional")["custo_hora"].to_dict()
        result["custo_ociosidade_rs"] = (
            result["profissional"].map(lambda p: custo_map.get(p, 0.0)) * result["no_shows"]
        )
    else:
        result["custo_ociosidade_rs"] = 0.0

    result = result.sort_values(
        by=["receita_perdida_rs", "no_shows"], ascending=False
    ).reset_index(drop=True)

    return result[columns]
