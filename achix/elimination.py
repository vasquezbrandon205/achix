"""
Disproof-first elimination engine.

"Proceed by trying to disprove hypotheses rather than prove them." (Heuer)

Each hypothesis is attacked from 4 angles:
    1. Contradictory evidence
    2. Missing expected evidence
    3. Assumption violations
    4. Structural impossibilities

Output: survival scores. The hypothesis with the fewest contradictions
survives — not the one with the most support.
"""

from dataclasses import dataclass, field
from typing import Dict, List

from achix.evidence import EvidenceGrade
from achix.matrix import ACHMatrix, Consistency


@dataclass
class SurvivalScore:
    hypothesis_id: str
    contradictions: int          # angle 1: hard contradictions
    missing_expected: int        # angle 2: expected evidence absent
    assumption_violations: int   # angle 3: violated assumptions (Layer 2)
    structural_blocks: int       # angle 4: structural impossibilities (Layer 3)
    total_strikes: float         # reliability-weighted total
    eliminated: bool = False
    disproof_notes: List[str] = field(default_factory=list)


# Strikes needed to eliminate. A single OBSERVED contradiction is damning;
# hypothesized contradictions are weaker. Threshold is on weighted strikes.
ELIMINATION_THRESHOLD = 2.0


class EliminationEngine:
    def __init__(self, matrix: ACHMatrix):
        self.matrix = matrix

    def attack(self, hypothesis_id: str) -> SurvivalScore:
        m = self.matrix
        notes: List[str] = []

        # Angle 1: contradictory evidence (all layers)
        contra_cells = [
            c for (eid, hid, layer), c in m.cells.items()
            if hid == hypothesis_id and c.consistency == Consistency.CONTRADICTS
        ]
        contradictions = len(contra_cells)
        for c in contra_cells:
            ev = m.evidence[c.evidence_id]
            notes.append(
                f"[contradiction] {c.evidence_id} (L{c.layer}, "
                f"{ev.grade.value}): {ev.description[:80]}")

        # Angle 2: missing expected evidence — UNKNOWN-grade items that
        # SHOULD exist if the hypothesis were true are strikes against it.
        # (The dog that didn't bark.)
        missing = 0
        for eid, ev in m.evidence.items():
            if ev.grade == EvidenceGrade.UNKNOWN and "expected" in ev.notes.lower():
                cell = m.get(eid, hypothesis_id, 1)
                if cell is None or cell.consistency != Consistency.CONTRADICTS:
                    missing += 1
                    notes.append(f"[missing expected] {eid}: {ev.description[:80]}")

        # Angle 3: assumption violations (Layer 2 contradictions)
        assumption_violations = sum(
            1 for c in contra_cells if c.layer == 2)
        # Angle 4: structural impossibilities (Layer 3 contradictions)
        structural_blocks = sum(
            1 for c in contra_cells if c.layer == 3)

        # Weighted strikes: an OBSERVED contradiction hits harder than a
        # HYPOTHESIZED one.
        total_strikes = sum(
            m.evidence[c.evidence_id].reliability() * m._layer_weight(c.layer)
            for c in contra_cells
        ) + 0.5 * missing

        eliminated = total_strikes >= ELIMINATION_THRESHOLD
        if eliminated:
            notes.append(
                f"ELIMINATED: {total_strikes:.2f} weighted strikes "
                f">= threshold {ELIMINATION_THRESHOLD}")

        return SurvivalScore(
            hypothesis_id=hypothesis_id,
            contradictions=contradictions,
            missing_expected=missing,
            assumption_violations=assumption_violations,
            structural_blocks=structural_blocks,
            total_strikes=round(total_strikes, 3),
            eliminated=eliminated,
            disproof_notes=notes,
        )

    def run_all(self) -> Dict[str, SurvivalScore]:
        return {hid: self.attack(hid) for hid in self.matrix.hypotheses}

    def survivors(self) -> List[str]:
        """Hypotheses not eliminated, ordered by fewest strikes."""
        scores = self.run_all()
        alive = [s for s in scores.values() if not s.eliminated]
        alive.sort(key=lambda s: s.total_strikes)
        return [s.hypothesis_id for s in alive]
