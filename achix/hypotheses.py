"""
Hypotheses and structured hypothesis generation.

ACHnX "Explode the Space": generate across 5 axes so the correct hypothesis
is in the set — Heuer's warning: "people are actually rather poor at
thinking of all the possibilities."
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class HypothesisKind(Enum):
    DIRECT = "direct"              # the obvious explanation
    INVERSE = "inverse"            # the opposite of the obvious
    HIDDEN_VARIABLE = "hidden"     # something unobserved drives the system
    DECEPTION = "deception"        # the system masks its true state
    STRUCTURAL = "structural"      # the model itself is wrong


@dataclass
class Hypothesis:
    id: str
    statement: str
    kind: HypothesisKind = HypothesisKind.DIRECT
    notes: str = ""

    def __post_init__(self):
        if not self.id:
            raise ValueError("Hypothesis requires an id")


def generation_checklist(hypotheses: List[Hypothesis]) -> dict:
    """Verify the hypothesis set covers all 5 generation axes.

    Returns which axes are covered and which are missing — a missing axis
    is a blind spot, not a pass.
    """
    covered = {h.kind for h in hypotheses}
    return {
        "covered": sorted(k.value for k in covered),
        "missing": sorted(k.value for k in HypothesisKind if k not in covered),
        "complete": len(covered) == len(HypothesisKind),
    }
