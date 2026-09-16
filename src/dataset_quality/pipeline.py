"""Orquestación mínima: la compuerta protege las etapas posteriores."""

from __future__ import annotations

from collections.abc import Callable

from dataset_quality.gate import has_failures
from dataset_quality.quality_policy import QualityGateReport


def continue_after_gate(
    report: QualityGateReport,
    split: Callable[[], None],
    export: Callable[[], None],
    promote_prod: Callable[[], None],
) -> bool:
    """Ejecuta etapas posteriores sólo si ningún check tiene estado ``fail``."""
    if has_failures(report):
        return False

    split()
    export()
    promote_prod()
    return True
