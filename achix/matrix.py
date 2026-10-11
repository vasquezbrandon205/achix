"""
The ACH matrix: 3-layer, weighted, disconfirmatory.

Layer 1 — Evidence vs Hypotheses (classic Heuer ACH)
Layer 2 — Assumptions vs Hypotheses (assumptions drive conclusions)
Layer 3 — Structural constraints vs Hypotheses (for equation-based work)

Scoring is DISCONFIRMATORY: the hypothesis with the FEWEST contradictions
wins, not the one with the most support. This is the heart of ACH.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple

from achix.evidence import EvidenceItem
from achix.hypotheses import Hypothesis


class Consistency(Enum):
    SUPPORTS = "+"        # consistent with the hypothesis
    CONTRADICTS = "-"     # inconsistent with the hypothesis
    AMBIGUOUS = "?"       # ambiguous / unclear
    IRRELEVANT = "0"      # not relevant to the hypothesis


@dataclass
class MatrixCell:
    evidence_id: str
    hypothesis_id: str
    consistency: Consistency
    layer: int = 1        # 1=evidence, 2=assumptions, 3=structural
    note: str = ""


class ACHMatrix:
    def __init__(self, hypotheses: List[Hypothesis], evidence: List[EvidenceItem]):
        self.hypotheses = {h.id: h for h in hypotheses}
        self.evidence = {e.id: e for e in evidence}
        self.cells: Dict[Tuple[str, str, int], MatrixCell] = {}

    def set(self, evidence_id: str, hypothesis_id: str, consistency: Consistency,
            layer: int = 1, note: str = "") -> None:
        if evidence_id not in self.evidence:
            raise KeyError(f"unknown evidence: {evidence_id}")
        if hypothesis_id not in self.hypotheses:
            raise KeyError(f"unknown hypothesis: {hypothesis_id}")
        if layer not in (1, 2, 3):
            raise ValueError("layer must be 1, 2, or 3")
        self.cells[(evidence_id, hypothesis_id, layer)] = MatrixCell(
            evidence_id, hypothesis_id, consistency, layer, note)

    def get(self, evidence_id: str, hypothesis_id: str, layer: int = 1):
        return self.cells.get((evidence_id, hypothesis_id, layer))

    def _layer_weight(self, layer: int) -> float:
        # Assumptions (L2) and structural constraints (L3) punch above
        # their weight: they silently steer conclusions.
        return {1: 1.0, 2: 1.25, 3: 1.25}[layer]

    def disconfirmation_score(self, hypothesis_id: str) -> float:
        """Weighted contradiction count. LOWER is better (fewer disproofs)."""
        total = 0.0
        for (eid, hid, layer), cell in self.cells.items():
            if hid != hypothesis_id:
                continue
            if cell.consistency == Consistency.CONTRADICTS:
                ev = self.evidence[eid]
                total += self._layer_weight(layer) * ev.reliability()
        return total

    def support_score(self, hypothesis_id: str) -> float:
        """Weighted support count. Informational only — ranking uses
        disconfirmation_score (disproof first)."""
        total = 0.0
        for (eid, hid, layer), cell in self.cells.items():
            if hid != hypothesis_id:
                continue
            if cell.consistency == Consistency.SUPPORTS:
                ev = self.evidence[eid]
                total += self._layer_weight(layer) * ev.reliability()
        return total

    def rank(self) -> List[Tuple[str, float, float]]:
        """Rank hypotheses: fewest contradictions first, then most support.

        Returns [(hypothesis_id, disconfirmation, support), ...].
        """
        scored = [
            (hid, self.disconfirmation_score(hid), self.support_score(hid))
            for hid in self.hypotheses
        ]
        scored.sort(key=lambda t: (t[1], -t[2]))
        return scored

    def contradictions(self, hypothesis_id: str) -> List[MatrixCell]:
        """All cells that contradict a hypothesis — the disproof list."""
        return [
            cell for (eid, hid, layer), cell in self.cells.items()
            if hid == hypothesis_id and cell.consistency == Consistency.CONTRADICTS
        ]

    def render_text(self) -> str:
        """Render the Layer-1 matrix as text (+/-/?/0)."""
        hids = list(self.hypotheses)
        eids = [eid for eid in self.evidence]
        header = "Evidence".ljust(28) + "".join(h.ljust(8) for h in hids)
        lines = [header, "-" * len(header)]
        for eid in eids:
            row = eid.ljust(28)
            for hid in hids:
                cell = self.get(eid, hid, 1)
                row += (cell.consistency.value if cell else " ").ljust(8)
            lines.append(row)
        lines.append("")
        lines.append("Legend: + consistent  - inconsistent  ? ambiguous  0 irrelevant")
        return "\n".join(lines)
