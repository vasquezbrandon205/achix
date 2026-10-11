"""
Honesty ledger — every claim carries its method label.

Labels:
    PROVEN       — mechanically verified, no judgment involved
    TESTED       — executed and observed, in-distribution
    HYPOTHESIZED — asserted without execution
    UNKNOWN      — relevant but unresolved

The ledger is append-only. A claim's label can be UPGRADED by evidence
(TESTED -> PROVEN) but never silently upgraded by narrative.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List


class MethodLabel(Enum):
    PROVEN = "PROVEN"
    TESTED = "TESTED"
    HYPOTHESIZED = "HYPOTHESIZED"
    UNKNOWN = "UNKNOWN"


# Allowed upgrades. Downgrades are always allowed (new counter-evidence).
_UPGRADES = {
    MethodLabel.UNKNOWN: {MethodLabel.HYPOTHESIZED, MethodLabel.TESTED},
    MethodLabel.HYPOTHESIZED: {MethodLabel.TESTED},
    MethodLabel.TESTED: {MethodLabel.PROVEN},
    MethodLabel.PROVEN: set(),
}


@dataclass
class LedgerEntry:
    claim: str
    label: MethodLabel
    evidence_ref: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat())
    history: List[str] = field(default_factory=list)

    def upgrade(self, new_label: MethodLabel, evidence_ref: str = "") -> None:
        if new_label == self.label:
            return
        if new_label not in _UPGRADES[self.label]:
            # Enum order is PROVEN(0) .. UNKNOWN(3): a lower index is a
            # stronger claim. Moving to a lower index is an upgrade attempt
            # and must go through the allowed path; moving down is a
            # downgrade and always allowed.
            order = list(MethodLabel)
            if order.index(new_label) < order.index(self.label):
                raise ValueError(
                    f"cannot upgrade {self.label.value} -> {new_label.value} "
                    f"without intermediate evidence")
        self.history.append(
            f"{self.timestamp}: {self.label.value} -> {new_label.value} "
            f"({evidence_ref})")
        self.label = new_label
        if evidence_ref:
            self.evidence_ref = evidence_ref


class HonestyLedger:
    def __init__(self):
        self.entries: List[LedgerEntry] = []

    def record(self, claim: str, label: MethodLabel,
               evidence_ref: str = "") -> LedgerEntry:
        entry = LedgerEntry(claim=claim, label=label, evidence_ref=evidence_ref)
        self.entries.append(entry)
        return entry

    def by_label(self, label: MethodLabel) -> List[LedgerEntry]:
        return [e for e in self.entries if e.label == label]

    def render_text(self) -> str:
        lines = ["HONESTY LEDGER", "=" * 60]
        for label in MethodLabel:
            items = self.by_label(label)
            if not items:
                continue
            lines.append(f"\n[{label.value}] ({len(items)})")
            for e in items:
                ref = f" — {e.evidence_ref}" if e.evidence_ref else ""
                lines.append(f"  - {e.claim}{ref}")
        return "\n".join(lines)
