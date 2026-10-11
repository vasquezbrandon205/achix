"""
Diagnosticity — the Information Value Index (IVI).

"Evidence is diagnostic when it influences your judgment on the relative
likelihood of the hypotheses." (Heuer)

IVI scores each evidence item on how much it DIFFERENTIATES hypotheses,
weighted by the evidence's own reliability grade. The top-ranked items are
the "linchpin evidence" — the few items that really drive the outcome.
"""

from typing import Dict, List, Tuple

from achix.evidence import EvidenceItem
from achix.hypotheses import Hypothesis
from achix.matrix import ACHMatrix, Consistency


def information_value_index(matrix: ACHMatrix, evidence_id: str) -> float:
    """IVI for one evidence item across all hypotheses (Layer 1).

    Differentiation power: an item is diagnostic when hypotheses DISAGREE
    about it. We count pairwise disagreements in consistency values,
    weighted by evidence reliability.

    IVI = reliability * (disagreeing pairs / total pairs)
    """
    ev = matrix.evidence[evidence_id]
    hids = list(matrix.hypotheses)
    if len(hids) < 2:
        return 0.0
    values = []
    for hid in hids:
        cell = matrix.get(evidence_id, hid, 1)
        values.append(cell.consistency if cell else Consistency.AMBIGUOUS)
    disagree = 0
    total = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            total += 1
            # Disagreement = different verdicts, ignoring AMBIGUOUS-vs-anything
            # (ambiguity is uninformative, not diagnostic)
            a, b = values[i], values[j]
            if a != b and Consistency.AMBIGUOUS not in (a, b):
                disagree += 1
    if total == 0:
        return 0.0
    return ev.reliability() * (disagree / total)


def rank_diagnostic_evidence(matrix: ACHMatrix) -> List[Tuple[str, float]]:
    """Rank all evidence by IVI, most diagnostic first."""
    scored = [
        (eid, information_value_index(matrix, eid))
        for eid in matrix.evidence
    ]
    scored.sort(key=lambda t: -t[1])
    return scored


def linchpin_evidence(matrix: ACHMatrix, top_n: int = 3) -> List[Tuple[str, float]]:
    """The few items of evidence that really drive the outcome."""
    return rank_diagnostic_evidence(matrix)[:top_n]
