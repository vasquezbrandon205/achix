"""
Level 5 transfer reasoning — the cross-domain bridge engine.

From ACHIX v1.2: Level 5 takes a structural match (L1-L4) and asks the
question that matters: "If this bridge is real, what information can
cross it?"

The critical design principle: Level 5 WITHHOLDS output when information
cannot cross the bridge. This is what separates a discovery engine from
an analogy decorator.

    "The hard part is not finding similarities. Humans are already pretty
     good at noticing those after the fact. The hard part is knowing which
     similarities matter." — B.M. Vasquez
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class BridgeLevel(Enum):
    """Which structural levels support the bridge."""
    L1_SYMBOLIC = "L1"      # equation match (variable renaming)
    L2_STRUCTURAL = "L2"   # equation equivalence (permutation search)
    L3_TOPOLOGICAL = "L3"  # phase diagram isomorphism
    L4_SCALING = "L4"      # critical exponents + universality classes


@dataclass
class StructuralSignal:
    """One piece of structural evidence for/against a bridge."""
    level: BridgeLevel
    supports: bool          # True=supporting signal, False=contradicting
    description: str = ""
    detail: str = ""


@dataclass
class TransferHypothesis:
    """The Level 5 output: what crosses the bridge, and how to kill it."""
    domain_a: str
    domain_b: str
    shared_mechanism: str = ""          # WHY they match
    variable_mapping: Dict[str, str] = field(default_factory=dict)  # A_var -> B_var
    transferable_methods: List[str] = field(default_factory=list)  # techniques that cross
    target_application: str = ""
    testable_predictions: List[str] = field(default_factory=list)
    boundary_conditions: List[str] = field(default_factory=list)   # when transfer is valid
    falsification_criteria: List[str] = field(default_factory=list)  # how to disprove
    transfer_score: float = 0.0
    is_actionable: bool = False
    withheld_reason: str = ""


@dataclass
class GateVerdict:
    actionable: bool
    reason: str
    blocking_signals: List[StructuralSignal] = field(default_factory=list)


class TransferGate:
    """Hard gate logic: only emit a hypothesis when the bridge can
    carry information. Otherwise WITHHOLD with a specific reason."""

    def evaluate(self, signals: List[StructuralSignal]) -> GateVerdict:
        supporting = [s for s in signals if s.supports]
        blocking = [s for s in signals if not s.supports]

        # Hard gate 1: explicit L3 contradiction (different transition types,
        # different order parameter behavior) kills the bridge.
        l3_blocks = [s for s in blocking if s.level == BridgeLevel.L3_TOPOLOGICAL]
        if l3_blocks:
            return GateVerdict(
                actionable=False,
                reason=("Level 3 contradiction: " +
                        "; ".join(s.description for s in l3_blocks) +
                        ". Information cannot cross the bridge."),
                blocking_signals=l3_blocks,
            )

        # Hard gate 2: explicit L4 contradiction (different critical
        # exponents, different universality classes) kills the bridge.
        l4_blocks = [s for s in blocking if s.level == BridgeLevel.L4_SCALING]
        if l4_blocks:
            return GateVerdict(
                actionable=False,
                reason=("Level 4 contradiction: " +
                        "; ".join(s.description for s in l4_blocks) +
                        ". Information cannot cross the bridge."),
                blocking_signals=l4_blocks,
            )

        # Soft gate: need at least one of —
        #   strong equation match (L1/L2), or
        #   topology match with >=3 signals (L3), or
        #   scaling match with >=2 signals (L4)
        l1l2 = [s for s in supporting
                if s.level in (BridgeLevel.L1_SYMBOLIC, BridgeLevel.L2_STRUCTURAL)]
        l3 = [s for s in supporting if s.level == BridgeLevel.L3_TOPOLOGICAL]
        l4 = [s for s in supporting if s.level == BridgeLevel.L4_SCALING]
        if not (l1l2 or len(l3) >= 3 or len(l4) >= 2):
            return GateVerdict(
                actionable=False,
                reason=("No sufficient bridge evidence at any level "
                        "(equation, topology, or scaling). "
                        "Information cannot cross the bridge."),
                blocking_signals=[],
            )

        return GateVerdict(actionable=True, reason="Bridge carries information.")

    def score(self, hypothesis: TransferHypothesis,
              signals: List[StructuralSignal]) -> float:
        """Transferability score (0-1). NOT a similarity score.

        Components (from ACHIX v1.2):
          variable map completeness  0.25
          method portability          0.25
          prediction specificity      0.25
          falsifiability              0.15
          cross-level consistency     0.10
        """
        n_vars = len(hypothesis.variable_mapping)
        var_score = 0.25 * min(n_vars / 8.0, 1.0)

        n_methods = len(hypothesis.transferable_methods)
        method_score = 0.25 * min(n_methods / 6.0, 1.0)

        # Numerical predictions worth more than qualitative ones.
        n_preds = len(hypothesis.testable_predictions)
        numerical = sum(1 for p in hypothesis.testable_predictions
                        if any(ch.isdigit() for ch in p))
        pred_score = 0.25 * min((numerical * 1.5 + (n_preds - numerical) * 0.5) / 5.0, 1.0)

        n_fals = len(hypothesis.falsification_criteria)
        fals_score = 0.15 * min(n_fals / 4.0, 1.0)

        levels = {s.level for s in signals if s.supports}
        cross_score = 0.10 if len(levels) >= 2 else 0.0

        return round(var_score + method_score + pred_score + fals_score + cross_score, 3)

    def build(self, domain_a: str, domain_b: str,
              signals: List[StructuralSignal], **kwargs) -> TransferHypothesis:
        """Run the gate; return an actionable hypothesis or a WITHHELD one."""
        verdict = self.evaluate(signals)
        h = TransferHypothesis(domain_a=domain_a, domain_b=domain_b, **kwargs)
        if not verdict.actionable:
            h.is_actionable = False
            h.withheld_reason = verdict.reason
            h.transfer_score = 0.0
            return h
        h.is_actionable = True
        h.transfer_score = self.score(h, signals)
        return h
