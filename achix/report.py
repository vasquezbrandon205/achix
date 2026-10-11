"""
ACH report — ranked hypotheses, diagnostic evidence, survival scores,
sensitivity, and the trigger map.

Output is probabilistic, not narrative: ranked hypotheses, scores,
assumption dependencies, and update triggers. Machine-readable and
human-readable.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from achix.diagnosticity import linchpin_evidence
from achix.elimination import EliminationEngine
from achix.matrix import ACHMatrix
from achix.sensitivity import LinchpinStressTest


@dataclass
class ACHReport:
    question: str
    ranking: List[str]                       # hypothesis ids, best first
    disconfirmation: Dict[str, float]
    support: Dict[str, float]
    diagnostic_evidence: List[tuple]         # (evidence_id, IVI)
    survival: Dict[str, object]              # hypothesis_id -> SurvivalScore
    fragility: Dict[str, List[str]]           # assumption_id -> flip effects
    triggers: List[str] = field(default_factory=list)  # trigger map

    def render_text(self, matrix: ACHMatrix) -> str:
        lines = []
        lines.append("=" * 70)
        lines.append("ACHIX ANALYSIS REPORT")
        lines.append("=" * 70)
        lines.append(f"\nQuestion: {self.question}\n")

        lines.append("RANKED HYPOTHESES (fewest contradictions first)")
        lines.append("-" * 70)
        for i, hid in enumerate(self.ranking, 1):
            h = matrix.hypotheses[hid]
            d = self.disconfirmation[hid]
            s = self.support[hid]
            surv = self.survival[hid]
            status = "ELIMINATED" if surv.eliminated else "SURVIVES"
            lines.append(
                f"{i}. {hid} [{status}] "
                f"(contradictions={d:.2f}, support={s:.2f})")
            lines.append(f"   {h.statement[:100]}")
        lines.append("")

        lines.append("MOST DIAGNOSTIC EVIDENCE (Information Value Index)")
        lines.append("-" * 70)
        for eid, ivi in self.diagnostic_evidence[:5]:
            ev = matrix.evidence[eid]
            lines.append(f"  {eid}: IVI={ivi:.3f} [{ev.grade.value}]")
            lines.append(f"    {ev.description[:90]}")
        lines.append("")

        lines.append("DISPROOF NOTES")
        lines.append("-" * 70)
        for hid in self.ranking:
            surv = self.survival[hid]
            if surv.disproof_notes:
                lines.append(f"  {hid}:")
                for n in surv.disproof_notes[:4]:
                    lines.append(f"    - {n[:100]}")
        lines.append("")

        lines.append("FRAGILITY (assumptions that flip the conclusion)")
        lines.append("-" * 70)
        if self.fragility:
            for aid, effects in self.fragility.items():
                lines.append(f"  {aid}:")
                for e in effects:
                    lines.append(f"    - {e}")
        else:
            lines.append("  No single assumption flip changes the ranking.")
        lines.append("")

        if self.triggers:
            lines.append("TRIGGER MAP (what would change your mind)")
            lines.append("-" * 70)
            for t in self.triggers:
                lines.append(f"  - {t}")
            lines.append("")

        lines.append("=" * 70)
        return "\n".join(lines)


def run_ach(question: str, matrix: ACHMatrix,
            assumption_ids: Optional[List[str]] = None,
            triggers: Optional[List[str]] = None) -> ACHReport:
    """Run the full ACHnX pipeline on a populated matrix."""
    ranked = matrix.rank()
    ranking = [hid for hid, _, _ in ranked]
    disconfirmation = {hid: d for hid, d, _ in ranked}
    support = {hid: s for hid, _, s in ranked}

    engine = EliminationEngine(matrix)
    survival = engine.run_all()

    diagnostic = linchpin_evidence(matrix, top_n=5)

    fragility: Dict[str, List[str]] = {}
    if assumption_ids:
        stress = LinchpinStressTest(matrix, assumption_ids)
        fragility = stress.fragility_report()

    return ACHReport(
        question=question,
        ranking=ranking,
        disconfirmation=disconfirmation,
        support=support,
        diagnostic_evidence=diagnostic,
        survival=survival,
        fragility=fragility,
        triggers=triggers or [],
    )
