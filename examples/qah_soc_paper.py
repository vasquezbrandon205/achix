"""
Worked example: ACHnX analysis of a condensed-matter paper.

Reconstruction of the ACHnX analysis of Qin et al. (2026),
"Engineering electrically-switchable quantum anomalous Hall states
by spin-orbit coupling" — hypotheses H1-H5, evidence E1-E9, and the
evidence x hypothesis matrix, as developed in the ACH-X working session.

Run: python examples/qah_soc_paper.py
"""

from achix import (
    ACHMatrix, Consistency, EliminationEngine, EvidenceGrade, EvidenceItem,
    Hypothesis, HypothesisKind, HonestyLedger, MethodLabel,
    generation_checklist, linchpin_evidence, run_ach,
)
from achix.sensitivity import LinchpinStressTest


def build() -> ACHMatrix:
    hypotheses = [
        Hypothesis("H1", "Authors' claim is correct: WSe2-induced Ising SOC "
                   "directly reshapes magnetization reversals and enables "
                   "new QAH switching behavior.", HypothesisKind.DIRECT),
        Hypothesis("H2", "SOC plays a role, but the dominant mechanism is "
                   "something else (strain, twist-angle homogeneity, disorder "
                   "reduction, substrate effects).", HypothesisKind.HIDDEN_VARIABLE),
        Hypothesis("H3", "The observed switching is intrinsic to tMBG and not "
                   "caused by WSe2; the SOC explanation is overstated.",
                   HypothesisKind.INVERSE),
        Hypothesis("H4", "Switching arises from mesoscopic defects, domain "
                   "wall pinning, or device geometry.", HypothesisKind.STRUCTURAL),
        Hypothesis("H5", "The interpretation of magnetization reversals is "
                   "incomplete or ambiguous; MR signatures do not uniquely "
                   "indicate spin-valley locking.", HypothesisKind.DECEPTION),
    ]

    evidence = [
        EvidenceItem("E1", "tMBG/WSe2 devices show well-quantized QAH states "
                     "at v=1 and v=3.", EvidenceGrade.OBSERVED,
                     source="paper: transport data"),
        EvidenceItem("E2", "New magnetization reversal appears in metallic "
                     "regime 1<v<2.", EvidenceGrade.OBSERVED,
                     source="paper: MR data"),
        EvidenceItem("E3", "Usual MR near v=3 disappears in tMBG/WSe2.",
                     EvidenceGrade.OBSERVED, source="paper: MR data"),
        EvidenceItem("E4", "Band structure calculations show strong Ising SOC "
                     "with WSe2 on BLG side.", EvidenceGrade.INFERRED,
                     source="paper: DFT calculations"),
        EvidenceItem("E5", "Quantum oscillation measurements confirm SOC.",
                     EvidenceGrade.OBSERVED, source="paper: oscillations"),
        EvidenceItem("E6", "Domain-wall-like features appear near MR "
                     "transitions.", EvidenceGrade.OBSERVED,
                     source="paper: imaging"),
        EvidenceItem("E7", "Twist-angle homogeneity unusually high "
                     "(Dq < 0.02 deg) — confounder: strengthens QAH regardless "
                     "of SOC.", EvidenceGrade.OBSERVED,
                     source="paper: characterization",
                     is_assumption=False),
        EvidenceItem("E8", "Mesoscopic defect charging observed near plateau "
                     "transitions.", EvidenceGrade.OBSERVED,
                     source="paper: imaging"),
        EvidenceItem("E9", "Model assumes SOC enforces spin-valley locking, "
                     "modifying magnetization sign changes.",
                     EvidenceGrade.HYPOTHESIZED, source="paper: model section",
                     is_assumption=True),
        EvidenceItem("A1", "Spin and orbital magnetization have similar "
                     "magnitude (needed for MR sign-change interpretation).",
                     EvidenceGrade.HYPOTHESIZED, is_assumption=True,
                     notes="linchpin assumption"),
    ]

    m = ACHMatrix(hypotheses, evidence)

    def put(eid, hid, c, note=""):
        m.set(eid, hid, Consistency[c], layer=1, note=note)

    # E1: QAH quantization — consistent with H1/H2/H3, irrelevant to H4
    put("E1", "H1", "SUPPORTS"); put("E1", "H2", "SUPPORTS")
    put("E1", "H3", "SUPPORTS"); put("E1", "H4", "IRRELEVANT")
    put("E1", "H5", "AMBIGUOUS")
    # E2: new MR at 1<v<2
    put("E2", "H1", "SUPPORTS"); put("E2", "H2", "SUPPORTS")
    put("E2", "H3", "CONTRADICTS"); put("E2", "H4", "SUPPORTS")
    put("E2", "H5", "AMBIGUOUS")
    # E3: missing MR at v=3
    put("E3", "H1", "SUPPORTS"); put("E3", "H2", "AMBIGUOUS")
    put("E3", "H3", "CONTRADICTS"); put("E3", "H4", "IRRELEVANT")
    put("E3", "H5", "AMBIGUOUS")
    # E4: SOC in band calc
    put("E4", "H1", "SUPPORTS"); put("E4", "H2", "CONTRADICTS")
    put("E4", "H3", "CONTRADICTS"); put("E4", "H4", "IRRELEVANT")
    put("E4", "H5", "IRRELEVANT")
    # E5: SOC in oscillations
    put("E5", "H1", "SUPPORTS"); put("E5", "H2", "CONTRADICTS")
    put("E5", "H3", "CONTRADICTS"); put("E5", "H4", "IRRELEVANT")
    put("E5", "H5", "IRRELEVANT")
    # E6: domain wall features
    put("E6", "H1", "IRRELEVANT"); put("E6", "H2", "IRRELEVANT")
    put("E6", "H3", "IRRELEVANT"); put("E6", "H4", "SUPPORTS")
    put("E6", "H5", "SUPPORTS")
    # E7: twist homogeneity (confounder)
    put("E7", "H1", "SUPPORTS"); put("E7", "H2", "SUPPORTS")
    put("E7", "H3", "SUPPORTS"); put("E7", "H4", "IRRELEVANT")
    put("E7", "H5", "AMBIGUOUS")
    # E8: defect charging
    put("E8", "H1", "IRRELEVANT"); put("E8", "H2", "IRRELEVANT")
    put("E8", "H3", "IRRELEVANT"); put("E8", "H4", "SUPPORTS")
    put("E8", "H5", "SUPPORTS")
    # E9: spin-valley locking model (assumption)
    put("E9", "H1", "SUPPORTS"); put("E9", "H2", "AMBIGUOUS")
    put("E9", "H3", "CONTRADICTS"); put("E9", "H4", "IRRELEVANT")
    put("E9", "H5", "AMBIGUOUS")

    # Layer 2: linchpin assumption A1
    m.set("A1", "H1", Consistency.SUPPORTS, layer=2,
          note="H1 needs spin~orbital magnetization for sign-change reading")
    m.set("A1", "H5", Consistency.CONTRADICTS, layer=2,
          note="if magnitudes differ, MR interpretation breaks toward H5")

    return m


def main():
    m = build()

    print("Hypothesis generation coverage:")
    cov = generation_checklist(list(m.hypotheses.values()))
    print(f"  covered: {cov['covered']}")
    print(f"  missing: {cov['missing']}\n")

    print(m.render_text())
    print()

    report = run_ach(
        question=("Does proximity-induced SOC from WSe2 causally modify "
                  "magnetization reversals and enable electrically switchable "
                  "QAH states in tMBG?"),
        matrix=m,
        assumption_ids=["A1", "E9"],
        triggers=[
            "Devices with tunable graphene-WSe2 alignment: if SOC strength "
            "correlates with MR behavior -> H1 strengthens.",
            "Pristine tMBG with ultra-high homogeneity showing the same MR "
            "pattern -> H1 weakens, H2 strengthens.",
            "Direct measurement of spin magnetization across v=1 and v=3 "
            "-> confirms or refutes spin-valley locking (A1).",
        ],
    )
    print(report.render_text(m))

    ledger = HonestyLedger()
    ledger.record("H1 survives all elimination attempts in this reconstruction",
                  MethodLabel.TESTED, "examples/qah_soc_paper.py run")
    ledger.record("Matrix values encode the analyst's reading of the paper, "
                  "not independent verification", MethodLabel.HYPOTHESIZED)
    ledger.record("ACH-for-paper-analysis generalizes to other papers",
                  MethodLabel.UNKNOWN)
    print(ledger.render_text())


if __name__ == "__main__":
    main()
