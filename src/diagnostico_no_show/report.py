"""Geração de relatórios Markdown e Excel."""

from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd

from diagnostico_no_show.models import DiagnosisResult

PathLike = Union[str, Path]


def _fmt_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_num(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def build_markdown_report(result: DiagnosisResult) -> str:
    """Monta o relatório executivo em Markdown."""
    s = result.summary

    lines = [
        "# Diagnóstico de No-Show",
        "",
        f"**Período:** {s['periodo_inicio']} a {s['periodo_fim']}",
        f"**Gerado em:** {result.generated_at}",
        "",
        "> Objetivo: quantificar **receita que não entrou** e **ociosidade de agenda** causada por no-show.",
        "",
        "---",
        "",
        "## Resumo executivo",
        "",
        "| Métrica | Valor |",
        "|---------|-------|",
        f"| Agendamentos analisados | {s['total_agendamentos']} |",
        f"| No-shows | {s['total_no_show']} |",
        f"| Comparecimentos | {s['total_compareceu']} |",
        f"| **Taxa de no-show** | **{_fmt_num(s['taxa_no_show_pct'])}%** |",
        f"| **Receita perdida** | **{_fmt_brl(s['receita_perdida_rs'])}** |",
        f"| Ticket médio do no-show | {_fmt_brl(s['ticket_medio_no_show_rs'])} |",
        f"| Custo de ociosidade | {_fmt_brl(s['custo_ociosidade_rs'])} |",
        f"| **Impacto total** | **{_fmt_brl(s['impacto_total_rs'])}** |",
        f"| Potencial de recuperação ({s['recovery_rate']:.0%}) | {_fmt_brl(s['potencial_recuperacao_rs'])} |",
        "",
        "### Confirmação faz diferença?",
        "",
        f"- Taxa de no-show **com** confirmação: {_fmt_num(s['taxa_ns_confirmado_pct'])}%",
        f"- Taxa de no-show **sem** confirmação: {_fmt_num(s['taxa_ns_nao_confirmado_pct'])}%",
        "",
        "---",
        "",
        "## Por profissional (mais receita perdida)",
        "",
    ]

    if result.by_profissional.empty:
        lines.append("_Sem dados._")
    else:
        lines.append(
            "| Profissional | Agendamentos | No-shows | Taxa | Receita perdida | Ociosidade |"
        )
        lines.append(
            "|--------------|-------------:|---------:|-----:|----------------:|-----------:|"
        )
        for _, row in result.by_profissional.head(10).iterrows():
            lines.append(
                f"| {row['profissional']} | {int(row['agendamentos'])} | {int(row['no_shows'])} | "
                f"{_fmt_num(row['taxa_no_show_pct'])}% | {_fmt_brl(row['receita_perdida_rs'])} | "
                f"{_fmt_brl(row['custo_ociosidade_rs'])} |"
            )

    lines.extend(["", "---", "", "## Por faixa horária", ""])

    if result.by_horario.empty:
        lines.append("_Sem dados._")
    else:
        lines.append("| Faixa | Agendamentos | No-shows | Taxa | Receita perdida |")
        lines.append("|-------|-------------:|---------:|-----:|----------------:|")
        for _, row in result.by_horario.head(10).iterrows():
            lines.append(
                f"| {row['faixa_hora']} | {int(row['agendamentos'])} | {int(row['no_shows'])} | "
                f"{_fmt_num(row['taxa_no_show_pct'])}% | {_fmt_brl(row['receita_perdida_rs'])} |"
            )

    lines.extend(["", "---", "", "## Por canal de agendamento", ""])

    if result.by_canal.empty:
        lines.append("_Sem dados._")
    else:
        lines.append("| Canal | Agendamentos | No-shows | Taxa | Receita perdida |")
        lines.append("|-------|-------------:|---------:|-----:|----------------:|")
        for _, row in result.by_canal.iterrows():
            lines.append(
                f"| {row['canal']} | {int(row['agendamentos'])} | {int(row['no_shows'])} | "
                f"{_fmt_num(row['taxa_no_show_pct'])}% | {_fmt_brl(row['receita_perdida_rs'])} |"
            )

    lines.extend(["", "---", "", "## Por serviço", ""])

    if result.by_servico.empty:
        lines.append("_Sem dados._")
    else:
        lines.append("| Serviço | Agendamentos | No-shows | Taxa | Receita perdida |")
        lines.append("|---------|-------------:|---------:|-----:|----------------:|")
        for _, row in result.by_servico.head(10).iterrows():
            lines.append(
                f"| {row['servico']} | {int(row['agendamentos'])} | {int(row['no_shows'])} | "
                f"{_fmt_num(row['taxa_no_show_pct'])}% | {_fmt_brl(row['receita_perdida_rs'])} |"
            )

    lines.extend(["", "---", "", "## Premissas", ""])
    for note in result.notes:
        lines.append(f"- {note}")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Próximas ações sugeridas",
            "",
            "1. **Confirmação obrigatória** nos canais com maior taxa de no-show.",
            "2. **Lista de espera** nos horários de pico para preencher buracos.",
            "3. **Lembrete automático** (WhatsApp) 24h e 2h antes.",
            "4. Revisar política de sinal/adiantamento nos serviços de ticket alto.",
            "5. Acompanhar a taxa por profissional — padrão diferente pede conversa, não punição.",
            "",
        ]
    )
    return "\n".join(lines)


def save_reports(
    result: DiagnosisResult,
    output_dir: PathLike,
    prefix: str = "diagnostico_no_show",
) -> dict:
    """Salva relatório Markdown + Excel detalhado."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    md_path = output_dir / f"{prefix}.md"
    xlsx_path = output_dir / f"{prefix}.xlsx"

    md_path.write_text(build_markdown_report(result), encoding="utf-8")

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        result.detail.to_excel(writer, sheet_name="detalhe", index=False)
        result.by_profissional.to_excel(writer, sheet_name="por_profissional", index=False)
        result.by_horario.to_excel(writer, sheet_name="por_horario", index=False)
        result.by_canal.to_excel(writer, sheet_name="por_canal", index=False)
        result.by_servico.to_excel(writer, sheet_name="por_servico", index=False)
        pd.DataFrame([result.summary]).to_excel(writer, sheet_name="resumo", index=False)

    return {"markdown": str(md_path), "excel": str(xlsx_path)}
