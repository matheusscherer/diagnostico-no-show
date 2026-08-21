"""Orquestração do diagnóstico de no-show."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from diagnostico_no_show.loader import load_agendamentos, load_profissionais
from diagnostico_no_show.metrics import compute_summary, rank_by
from diagnostico_no_show.models import DiagnosisResult, NoShowPolicy


def run_diagnosis(
    agendamentos_path: Path,
    profissionais_path: Path | None = None,
    policy: NoShowPolicy | None = None,
) -> DiagnosisResult:
    """Executa o diagnóstico completo."""
    policy = policy or NoShowPolicy()

    agendamentos = load_agendamentos(agendamentos_path)
    profissionais = load_profissionais(profissionais_path)

    summary = compute_summary(agendamentos, profissionais, policy)

    by_profissional = rank_by(agendamentos, "profissional", profissionais)
    by_horario = rank_by(agendamentos, "faixa_hora")
    by_canal = rank_by(agendamentos, "canal")
    by_servico = rank_by(agendamentos, "servico")

    notes = [
        "Receita perdida = soma do ticket dos status no_show.",
        "Taxa de no-show = no_shows / (compareceu + no_show). Cancelados e remarcados ficam de fora da taxa.",
        "Custo de ociosidade assume 1 slot ≈ 1 hora do profissional (simplificação consciente).",
        f"Potencial de recuperação usa taxa conservadora de {policy.recovery_rate:.0%} (lista de espera / confirmação).",
        "Dados de exemplo são sintéticos.",
    ]

    return DiagnosisResult(
        detail=agendamentos,
        summary=summary,
        by_profissional=by_profissional,
        by_horario=by_horario,
        by_canal=by_canal,
        by_servico=by_servico,
        policy=policy,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        notes=notes,
    )
