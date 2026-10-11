"""
Worked example: Level 5 transfer reasoning on SIR <-> Percolation.

Reconstruction of the ACHIX v1.2 TransferHypothesis for the
epidemiology <-> statistical physics bridge: shared 3d-percolation
universality class, explicit variable mapping, testable predictions
with critical exponents, and independent falsification criteria.

Also demonstrates the hard gate: the Water <-> Ferromagnet bridge
is WITHHELD on a Level 3 contradiction.

Run: python examples/sir_percolation.py
"""

from achix.transfer import (
    BridgeLevel, StructuralSignal, TransferGate, TransferHypothesis,
)


def sir_percolation_signals():
    return [
        StructuralSignal(BridgeLevel.L3_TOPOLOGICAL, True,
                         "isomorphic phase structure: disease-free <-> "
                         "disconnected, epidemic <-> giant component"),
        StructuralSignal(BridgeLevel.L3_TOPOLOGICAL, True,
                         "outbreak size distribution matches cluster size "
                         "distribution form"),
        StructuralSignal(BridgeLevel.L3_TOPOLOGICAL, True,
                         "threshold behavior at Tc (epidemic) <-> pc "
                         "(percolation)"),
        StructuralSignal(BridgeLevel.L4_SCALING, True,
                         "shared 3d-percolation universality class: "
                         "beta=0.418, gamma=1.8, nu=0.876"),
        StructuralSignal(BridgeLevel.L4_SCALING, True,
                         "same RG fixed point governs critical behavior"),
    ]


def water_ferromagnet_signals():
    # Adversarial pair: the gate must WITHHOLD.
    return [
        StructuralSignal(BridgeLevel.L3_TOPOLOGICAL, True,
                         "both exhibit phase transitions"),
        StructuralSignal(BridgeLevel.L3_TOPOLOGICAL, False,
                         "different order parameter behavior: density "
                         "discontinuity vs magnetization"),
    ]


def main():
    gate = TransferGate()

    print("=" * 70)
    print("BRIDGE 1: SIR (epidemiology) <-> Percolation (statistical physics)")
    print("=" * 70)
    h = gate.build(
        domain_a="SIR epidemiology",
        domain_b="3d percolation (statistical physics)",
        signals=sir_percolation_signals(),
        shared_mechanism=(
            "Both systems share a 3d-percolation phase transition with "
            "isomorphic topology. Same universality class, same RG fixed "
            "point governs critical behavior."),
        variable_mapping={
            "disease-free phase": "disconnected phase",
            "epidemic phase": "giant component phase",
            "infected fraction": "giant component size (S_inf)",
            "epidemic threshold (Tc)": "percolation threshold (pc)",
            "outbreak size": "cluster size distribution",
        },
        transferable_methods=[
            "finite-size scaling", "renormalization group",
            "crossover analysis", "cluster statistics",
            "critical slowing-down diagnostics", "universality checks",
        ],
        target_application="epidemic forecasting near threshold",
        testable_predictions=[
            "giant component size scales as |p-pc|^beta, beta=0.418",
            "susceptibility diverges as |p-pc|^-gamma, gamma=1.8",
            "correlation length scales as |p-pc|^-nu, nu=0.876",
            "transition at same topological conditions (isomorphic phases)",
            "critical slowing down near transition",
        ],
        boundary_conditions=[
            "valid near the transition only",
            "requires large-system limit for scaling laws",
        ],
        falsification_criteria=[
            "measured exponents differ from beta=0.418/gamma=1.8/nu=0.876 "
            "(tol +-0.1) -> bridge FALSE",
            "finite-size scaling not of 3d-percolation form -> method "
            "transfer invalid",
            "transition at different topological conditions -> topological "
            "bridge FALSE",
            "no predicted onset behavior in observables -> phase "
            "correspondence invalid",
        ],
    )
    print(f"actionable: {h.is_actionable}")
    print(f"transfer score: {h.transfer_score}")
    print(f"mechanism: {h.shared_mechanism}")
    print(f"variable mappings: {len(h.variable_mapping)}")
    print(f"predictions: {len(h.testable_predictions)}")
    print(f"falsification routes: {len(h.falsification_criteria)}")
    print()

    print("=" * 70)
    print("BRIDGE 2: Water boiling <-> Ferromagnet (adversarial — must WITHHOLD)")
    print("=" * 70)
    h2 = gate.build(
        domain_a="water boiling",
        domain_b="ferromagnet",
        signals=water_ferromagnet_signals(),
    )
    print(f"actionable: {h2.is_actionable}")
    if not h2.is_actionable:
        print(f"WITHHELD — {h2.withheld_reason}")
    assert not h2.is_actionable, "hard gate failed: adversarial bridge emitted!"
    print("\nHard gate holds: superficial similarity did not produce a hypothesis.")


if __name__ == "__main__":
    main()
