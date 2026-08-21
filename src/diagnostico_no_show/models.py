"""Modelos de domínio do diagnóstico de no-show."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class NoShowPolicy:
    """Parâmetros de política do diagnóstico."""

    # Janela em dias usada para contextualizar o relatório (informativo)
    window_days: int = 30
    # Fração conservadora de no-shows que poderiam ser recuperados
    # com lista de espera / confirmação reforçada
    recovery_rate: float = 0.25

    def __post_init__(self) -> None:
        if self.window_days <= 0:
            raise ValueError("window_days deve ser > 0")
        if not 0.0 <= self.recovery_rate <= 1.0:
            raise ValueError("recovery_rate deve estar entre 0 e 1")


@dataclass
class DiagnosisResult:
    """Resultado completo do diagnóstico."""

    detail: pd.DataFrame
    summary: dict
    by_profissional: pd.DataFrame
    by_horario: pd.DataFrame
    by_canal: pd.DataFrame
    by_servico: pd.DataFrame
    policy: NoShowPolicy
    generated_at: str
    notes: list[str] = field(default_factory=list)

    @property
    def receita_perdida(self) -> float:
        return float(self.summary.get("receita_perdida_rs", 0.0))

    @property
    def custo_ociosidade(self) -> float:
        return float(self.summary.get("custo_ociosidade_rs", 0.0))

    @property
    def impacto_total(self) -> float:
        return self.receita_perdida + self.custo_ociosidade
