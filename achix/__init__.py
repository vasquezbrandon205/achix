"""
ACHIX — Analysis of Competing Hypotheses for scientific discovery.

Computational Heuer-style ACH (hypothesis x evidence matrix, disconfirmatory
scoring, evidence grading) applied to science — plus Level 5 transfer reasoning
for cross-domain structural bridges.

Method status labels: PROVEN / TESTED / HYPOTHESIZED / UNKNOWN.
"""

from achix.evidence import EvidenceGrade, EvidenceItem
from achix.hypotheses import Hypothesis, HypothesisKind, generation_checklist
from achix.matrix import ACHMatrix, Consistency
from achix.diagnosticity import information_value_index, linchpin_evidence, rank_diagnostic_evidence
from achix.elimination import EliminationEngine, SurvivalScore
from achix.sensitivity import LinchpinStressTest
from achix.transfer import TransferHypothesis, TransferGate
from achix.ledger import HonestyLedger, MethodLabel
from achix.report import ACHReport, run_ach

__version__ = "1.0.0"
__all__ = [
    "EvidenceGrade",
    "EvidenceItem",
    "Hypothesis",
    "HypothesisKind",
    "generation_checklist",
    "ACHMatrix",
    "Consistency",
    "information_value_index",
    "linchpin_evidence",
    "rank_diagnostic_evidence",
    "EliminationEngine",
    "SurvivalScore",
    "LinchpinStressTest",
    "TransferHypothesis",
    "TransferGate",
    "HonestyLedger",
    "MethodLabel",
    "ACHReport",
    "run_ach",
]
