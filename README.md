# ACHIX — Analysis of Competing Hypotheses for Science

Computational Heuer-style ACH (hypothesis × evidence matrix, disconfirmatory scoring, evidence grading) applied to **scientific discovery** — plus Level 5 transfer reasoning for cross-domain structural bridges.

> "The hard part is not finding similarities. Humans are already pretty good at noticing those after the fact. The hard part is knowing which similarities matter." — B.M. Vasquez

## The problem

Most analysis — human or machine — picks one explanation and confirms it. ACH (Richards Heuer's *Analysis of Competing Hypotheses*) does the opposite: maintain **multiple competing hypotheses**, score them by **disproof rather than proof**, and identify the **few pieces of evidence that actually distinguish** between them.

ACH software exists for intelligence analysis. **Nobody had built it for science.** ACHIX is the crossover: Heuer-style adjudication (hypothesis×evidence matrix, disconfirmatory scoring, evidence grading) applied to research papers, competing mechanisms, and cross-domain structural analogies.

## What it does

**ACHnX engine** — modernized ACH in 8 components:
1. **Hypothesis generation** across 5 axes (direct, inverse, hidden-variable, deception, structural) — so the right hypothesis is in the set
2. **Evidence mapping** — "everything is evidence": data, missing data, assumptions, constraints, failure modes
3. **Diagnosticity (IVI)** — Information Value Index ranks evidence by how much it *differentiates* hypotheses
4. **3-layer matrix** — evidence×hypotheses, assumptions×hypotheses, structural-constraints×hypotheses
5. **Disproof-first elimination** — attack each hypothesis from 4 angles; fewest contradictions wins
6. **Linchpin stress test** — flip/weaken/strengthen/remove/replace key assumptions; if the ranking flips, the conclusion is fragile and the report says so
7. **Probabilistic output** — ranked hypotheses, survival scores, not narratives
8. **Trigger map** — what future data would change your mind (a living analysis, not a one-time verdict)

**Level 5 transfer reasoning** — for cross-domain bridges (spin glass ↔ Hopfield nets, SIR ↔ percolation):
- Builds a `TransferHypothesis`: shared mechanism, explicit variable mapping, transferable methods, numerical predictions, falsification criteria
- **Hard gate**: WITHHOLDS output when structural evidence contradicts the bridge — "information cannot cross the bridge." A withheld "no" is a first-class result.

**Honesty ledger** — every claim carries a method label: `PROVEN` / `TESTED` / `HYPOTHESIZED` / `UNKNOWN`. Labels upgrade only with evidence, never with narrative.

## Quick start

```bash
pip install -r requirements.txt
python examples/qah_soc_paper.py   # ACHnX on a real condensed-matter paper
python examples/sir_percolation.py # Level 5 transfer bridge + hard-gate demo
python -m pytest tests/            # 13 tests
```

## Worked examples

- **`examples/qah_soc_paper.py`** — full ACHnX reconstruction of a real analysis (Qin et al. 2026, SOC-induced QAH states): 5 hypotheses, 10 evidence items, matrix, diagnosticity ranking, elimination (H3 ruled out), sensitivity (conclusion fragile to assumption A1), trigger map.
- **`examples/sir_percolation.py`** — SIR↔percolation transfer hypothesis (score 0.906, 5 predictions, 4 falsification routes) plus the adversarial Water↔Ferromagnet pair, which the hard gate correctly WITHHOLDS on a Level 3 contradiction.

## Honest calibration

- Heuer's ACH and ACH software **exist for intelligence work** (PARC ACH 2.0, several open implementations). The novelty here is the **science crossover**: disconfirmatory adjudication for papers, mechanisms, and cross-domain bridges — plus the hard-gated transfer layer.
- The worked examples are **reconstructions** of analyses, not independent blind runs. Matrix values encode the analyst's reading.
- Level 5 is **template-structured**, not free-form generation — constrained creativity in exchange for falsifiability.
- This generates **hypothesis cards**, not validated discoveries. The next step is a validation harness (simulations, empirical data, literature checks).

## Paradigm

ACHIX is one instance of a broader thesis: **falsification-driven epistemic architecture** — systems that maintain competing hypotheses and explicit uncertainty instead of collapsing to a single answer. See `docs/PARADIGM.md`. Companion: [AIX](https://github.com/vasquezbrandon205/aix) (adversarial hypothesis competition for symbolic discovery).

## Citation

```bibtex
@software{vasquez2026achix,
  author = {Vasquez, Brandon Manuel},
  title = {ACHIX: Analysis of Competing Hypotheses for Science},
  year = {2026},
  url = {https://github.com/vasquezbrandon205/achix}
}
```

## License

Apache 2.0 — see [LICENSE](LICENSE).
