"""Caminhos e constantes padrão."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AGENDAMENTOS_PATH = ROOT / "data" / "raw" / "agendamentos.csv"
DEFAULT_PROFISSIONAIS_PATH = ROOT / "data" / "raw" / "profissionais.csv"
DEFAULT_OUTPUT_DIR = ROOT / "outputs"

STATUS_NO_SHOW = "no_show"
STATUS_COMPARECEU = "compareceu"
STATUS_CANCELADO = "cancelado"
STATUS_REMARCADO = "remarcado"

VALID_STATUS = {
    STATUS_NO_SHOW,
    STATUS_COMPARECEU,
    STATUS_CANCELADO,
    STATUS_REMARCADO,
}
