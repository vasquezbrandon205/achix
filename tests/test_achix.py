"""Tests for the ACHIX engine: matrix scoring, elimination, gates, ledger."""

import pytest

from achix import (
    ACHMatrix, Consistency, EliminationEngine, EvidenceGrade, EvidenceItem,
    HonestyLedger, Hypothesis, HypothesisKind, MethodLabel, TransferGate,
    generation_checklist, information_value_index, run_ach,
)
from achix.sensitivity import LinchpinStressTest
from achix.transfer import BridgeLevel, StructuralSignal


def tiny_matrix():
    hs = [
        Hypothesis("H1", "first explanation", HypothesisKind.DIRECT),
        Hypothesis("H2", "rival explanation", HypothesisKind.INVERSE),
    ]
    es = [
        EvidenceItem("E1", "supports H1, contradicts H2",
                     EvidenceGrade.OBSERVED),
        EvidenceItem("E2", "supports both", EvidenceGrade.OBSERVED),
        EvidenceItem("E3", "irrelevant", EvidenceGrade.OBSERVED),
    ]
    m = ACHMatrix(hs, es)
    m.set("E1", "H1", Consistency.SUPPORTS)
    m.set("E1", "H2", Consistency.CONTRADICTS)
    m.set("E2", "H1", Consistency.SUPPORTS)
    m.set("E2", "H2", Consistency.SUPPORTS)
    return m


def test_ranking_prefers_fewer_contradictions():
    m = tiny_matrix()
    ranking = [hid for hid, _, _ in m.rank()]
    assert ranking[0] == "H1"  # H2 has a contradiction, H1 has none


def test_support_does_not_outrank_disconfirmation():
    # Even with overwhelming support, a contradiction loses to zero
    # contradictions. Disproof first.
    m = tiny_matrix()
    assert m.disconfirmation_score("H2") > m.disconfirmation_score("H1")


def test_ivi_rewards_differentiation():
    m = tiny_matrix()
    # E1 splits the hypotheses -> diagnostic. E2 agrees -> not diagnostic.
    assert information_value_index(m, "E1") > information_value_index(m, "E2")
    assert information_value_index(m, "E2") == 0.0


def test_ivi_discounts_unreliable_evidence():
    m = tiny_matrix()
    m.evidence["E1"].grade = EvidenceGrade.HYPOTHESIZED
    ivi_hyp = information_value_index(m, "E1")
    m.evidence["E1"].grade = EvidenceGrade.OBSERVED
    ivi_obs = information_value_index(m, "E1")
    assert ivi_obs > ivi_hyp > 0


def test_generation_checklist_finds_blind_spots():
    hs = [Hypothesis("H1", "x", HypothesisKind.DIRECT)]
    cov = generation_checklist(hs)
    assert not cov["complete"]
    assert HypothesisKind.STRUCTURAL.value in cov["missing"]


def test_elimination_kills_contradicted_hypothesis():
    m = tiny_matrix()
    # Add a second observed contradiction to push H2 over the threshold.
    m2_ev = EvidenceItem("E4", "also contradicts H2", EvidenceGrade.OBSERVED)
    m.evidence["E4"] = m2_ev
    m.set("E4", "H2", Consistency.CONTRADICTS)
    engine = EliminationEngine(m)
    scores = engine.run_all()
    assert scores["H2"].eliminated
    assert not scores["H1"].eliminated
    assert engine.survivors() == ["H1"]


def test_transfer_gate_withholds_on_l3_contradiction():
    gate = TransferGate()
    signals = [
        StructuralSignal(BridgeLevel.L3_TOPOLOGICAL, True, "both transition"),
        StructuralSignal(BridgeLevel.L3_TOPOLOGICAL, False,
                         "different order parameters"),
    ]
    h = gate.build("A", "B", signals)
    assert not h.is_actionable
    assert "Level 3 contradiction" in h.withheld_reason


def test_transfer_gate_withholds_on_l4_contradiction():
    gate = TransferGate()
    signals = [
        StructuralSignal(BridgeLevel.L4_SCALING, False,
                         "different critical exponents"),
    ]
    h = gate.build("A", "B", signals)
    assert not h.is_actionable
    assert "Level 4 contradiction" in h.withheld_reason


def test_transfer_gate_withholds_on_insufficient_evidence():
    gate = TransferGate()
    h = gate.build("A", "B", [
        StructuralSignal(BridgeLevel.L3_TOPOLOGICAL, True, "vague similarity"),
    ])
    assert not h.is_actionable
    assert "No sufficient bridge evidence" in h.withheld_reason


def test_transfer_gate_passes_strong_bridge():
    gate = TransferGate()
    signals = [
        StructuralSignal(BridgeLevel.L3_TOPOLOGICAL, True, "s1"),
        StructuralSignal(BridgeLevel.L3_TOPOLOGICAL, True, "s2"),
        StructuralSignal(BridgeLevel.L3_TOPOLOGICAL, True, "s3"),
        StructuralSignal(BridgeLevel.L4_SCALING, True, "same exponents"),
        StructuralSignal(BridgeLevel.L4_SCALING, True, "same RG fixed point"),
    ]
    h = gate.build(
        "A", "B", signals,
        variable_mapping={f"a{i}": f"b{i}" for i in range(8)},
        transferable_methods=[f"m{i}" for i in range(6)],
        testable_predictions=["x scales as t^0.5", "y diverges", "z ~ 1.8"],
        falsification_criteria=["f1", "f2", "f3", "f4"],
    )
    assert h.is_actionable
    assert 0.0 < h.transfer_score <= 1.0


def test_ledger_upgrade_rules():
    ledger = HonestyLedger()
    e = ledger.record("claim", MethodLabel.HYPOTHESIZED)
    e.upgrade(MethodLabel.TESTED, "ran it")
    assert e.label == MethodLabel.TESTED
    # Skip-level upgrade without evidence is rejected.
    e2 = ledger.record("claim2", MethodLabel.UNKNOWN)
    with pytest.raises(ValueError):
        e2.upgrade(MethodLabel.PROVEN)
    # Downgrade always allowed.
    e.upgrade(MethodLabel.HYPOTHESIZED, "counter-evidence")
    assert e.label == MethodLabel.HYPOTHESIZED


def test_stress_test_detects_fragility():
    m = tiny_matrix()
    # Make E1 an assumption so it can be stress-tested.
    m.set("E1", "H1", Consistency.SUPPORTS, layer=2)
    m.set("E1", "H2", Consistency.CONTRADICTS, layer=2)
    stress = LinchpinStressTest(m, ["E1"])
    frag = stress.fragility_report()
    # Flipping E1's verdicts should change the ranking.
    assert "E1" in frag


def test_full_pipeline_runs():
    m = tiny_matrix()
    report = run_ach("which explanation?", m, triggers=["if E1 is wrong, flip"])
    assert report.ranking[0] == "H1"
    text = report.render_text(m)
    assert "RANKED HYPOTHESES" in text
    assert "TRIGGER MAP" in text
