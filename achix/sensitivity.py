"""
Linchpin stress test (sensitivity analysis 2.0).

"When analysis turns out to be wrong, it is often because of key
assumptions that went unchallenged." (Heuer)

Each linchpin assumption is stress-tested 5 ways: flip it, weaken it,
strengthen it, remove it, replace it. If flipping one assumption flips
the ranking, the conclusion is FRAGILE and the report must say so.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple

from achix.evidence import EvidenceGrade
from achix.matrix import ACHMatrix, Consistency


@dataclass
class StressResult:
    assumption_id: str
    operation: str          # flip / weaken / strengthen / remove / replace
    ranking_before: List[str]
    ranking_after: List[str]
    ranking_changed: bool
    new_leader: str


STRESS_OPERATIONS = ["flip", "weaken", "strengthen", "remove", "replace"]


class LinchpinStressTest:
    """Perturb assumptions and watch the ranking.

    Because consistency values are discrete (+/-/0/?), the stress operations
    are modeled as targeted edits to the assumption's matrix cells:
      flip:       swap + <-> - for that assumption across hypotheses
      weaken:     downgrade grade OBSERVED->INFERRED->HYPOTHESIZED (halves weight)
      strengthen: no-op on values, but recorded (tests narrative dependence)
      remove:     delete the assumption's cells
      replace:    flip + mark grade HYPOTHESIZED (alternative assumption)
    """

    def __init__(self, matrix: ACHMatrix, assumption_ids: List[str]):
        self.matrix = matrix
        self.assumption_ids = assumption_ids

    def _ranking(self, matrix: ACHMatrix) -> List[str]:
        return [hid for hid, _, _ in matrix.rank()]

    def _clone_with_edit(self, assumption_id: str, operation: str) -> ACHMatrix:
        import copy
        m = copy.deepcopy(self.matrix)
        if operation == "remove":
            for key in [k for k in m.cells if k[0] == assumption_id]:
                del m.cells[key]
            return m
        for (eid, hid, layer), cell in list(m.cells.items()):
            if eid != assumption_id:
                continue
            if operation == "flip":
                if cell.consistency == Consistency.SUPPORTS:
                    cell.consistency = Consistency.CONTRADICTS
                elif cell.consistency == Consistency.CONTRADICTS:
                    cell.consistency = Consistency.SUPPORTS
            elif operation == "replace":
                if cell.consistency == Consistency.SUPPORTS:
                    cell.consistency = Consistency.CONTRADICTS
                elif cell.consistency == Consistency.CONTRADICTS:
                    cell.consistency = Consistency.SUPPORTS
                m.evidence[eid].grade = EvidenceGrade.HYPOTHESIZED
            elif operation == "weaken":
                g = m.evidence[eid].grade
                if g == EvidenceGrade.OBSERVED:
                    m.evidence[eid].grade = EvidenceGrade.INFERRED
                elif g == EvidenceGrade.INFERRED:
                    m.evidence[eid].grade = EvidenceGrade.HYPOTHESIZED
            # strengthen: narrative check only, no mechanical change
        return m

    def run(self) -> List[StressResult]:
        before = self._ranking(self.matrix)
        results = []
        for aid in self.assumption_ids:
            for op in STRESS_OPERATIONS:
                perturbed = self._clone_with_edit(aid, op)
                after = self._ranking(perturbed)
                changed = after != before
                results.append(StressResult(
                    assumption_id=aid,
                    operation=op,
                    ranking_before=before,
                    ranking_after=after,
                    ranking_changed=changed,
                    new_leader=after[0] if after else "",
                ))
        return results

    def fragility_report(self) -> Dict[str, List[str]]:
        """Which assumptions flip the conclusion, and how."""
        fragile: Dict[str, List[str]] = {}
        for r in self.run():
            if r.ranking_changed and r.operation in ("flip", "remove"):
                fragile.setdefault(r.assumption_id, []).append(
                    f"{r.operation} -> leader becomes {r.new_leader}")
        return fragile
