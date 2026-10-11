"""
Evidence taxonomy and evidence items.

Grades (from the ACHIX methodology):
    OBSERVED      — directly measured / quoted from source
    INFERRED      — derived by reasoning from observed items
    HYPOTHESIZED  — assumed for the analysis, not established
    UNKNOWN       — relevant but currently missing
    CONTRADICTED  — contradicted by other evidence

The grade drives reliability weighting in diagnosticity scoring:
observed evidence counts more than hypothesized evidence.
"""

from dataclasses import dataclass, field
from enum import Enum


class EvidenceGrade(Enum):
    OBSERVED = "OBSERVED"
    INFERRED = "INFERRED"
    HYPOTHESIZED = "HYPOTHESIZED"
    UNKNOWN = "UNKNOWN"
    CONTRADICTED = "CONTRADICTED"


# Reliability weight per grade — used when scoring diagnosticity.
# OBSERVED counts fully; HYPOTHESIZED counts at half; UNKNOWN contributes
# nothing until resolved. CONTRADICTED evidence is a red flag, not support.
GRADE_RELIABILITY = {
    EvidenceGrade.OBSERVED: 1.0,
    EvidenceGrade.INFERRED: 0.8,
    EvidenceGrade.HYPOTHESIZED: 0.5,
    EvidenceGrade.UNKNOWN: 0.0,
    EvidenceGrade.CONTRADICTED: 0.0,
}


@dataclass
class EvidenceItem:
    """A single piece of evidence or assumption.

    ACHnX principle: "Everything is evidence" — observed data, missing data
    (the dog that didn't bark), model assumptions, system constraints,
    prior equations, known failure modes, incentives, structural pressures.
    """

    id: str
    description: str
    grade: EvidenceGrade = EvidenceGrade.OBSERVED
    source: str = ""          # quote, figure number, or derivation note
    is_assumption: bool = False  # assumptions are evidence too (ACHnX 2.0)
    notes: str = ""

    def reliability(self) -> float:
        return GRADE_RELIABILITY[self.grade]

    def __post_init__(self):
        if not self.id:
            raise ValueError("EvidenceItem requires an id")
