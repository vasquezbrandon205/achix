# The Paradigm: Falsification-Driven Epistemic Architecture

Most AI systems — and most human analysis — collapse to a single answer. One best-fit equation. One top hypothesis. One confidence score. The alternatives die silently, the assumptions stay buried, and the uncertainty gets rounded off.

This is a paradigm for building systems that don't do that.

## The thesis

**Maintain competing hypotheses. Attack them. Grade your evidence. Withhold output when you can't justify it. Report what would change your mind.**

Five primitives, composable across domains:

1. **Hypothesis sets, not point estimates.** The output is a ranked set of structurally distinct competitors, each with a survival score. (ACHIX: `Hypothesis` + 5-axis generation. AIX: competing equation families.)
2. **Disconfirmatory scoring.** Rank by fewest contradictions, not most support. Confirmation is cheap; survival is expensive. (ACHIX: `ACHMatrix.disconfirmation_score`. AIX: property sieve rejects.)
3. **Graded evidence.** Every claim carries its epistemic status: `OBSERVED` / `INFERRED` / `HYPOTHESIZED` / `UNKNOWN` / `CONTRADICTED`. Uncertainty is a first-class output with the same status as a prediction — not a footnote. (ACHIX: `EvidenceGrade`, `HonestyLedger`. AIX: PROVEN/TESTED/HYPOTHESIZED/UNKNOWN method labels.)
4. **Adversarial discrimination.** Don't just fit hypotheses — find the inputs that maximally separate them, then go get that data. (ACHIX: diagnosticity/IVI + trigger maps. AIX: discriminator synthesizing x*.)
5. **Withholding as a result.** "I don't know" and "the bridge doesn't hold" are outputs, not failures. A system that can't say no will decorate noise with confidence. (ACHIX: transfer hard gate. AIX: sieve rejection.)

## Instances

| System | Domain | Hypotheses | Adjudication | Withholding |
|---|---|---|---|---|
| ACHIX | paper analysis, cross-domain bridges | H1..Hn competing explanations | ACH matrix, disproof-first | transfer hard gate |
| AIX | symbolic discovery | competing equation families | property sieve, adversarial x* | sieve rejection |
| MUSE-ICF | binary reverse engineering | candidate indirect-call targets | evidence-graded resolution | honest UNKNOWNs |

## What it's not

- Not Bayesianism with extra steps. Priors are fine; the point here is the *architecture*: explicit competitors, explicit grades, explicit withholding.
- Not "AI safety" as usually meant. This is epistemic safety: systems that know what they don't know and say so.
- Not a single algorithm. It's a design stance — like "test-driven development" was a stance, not a library.

## Open problems

- **Validation harness**: hypothesis cards are cheap; checking them against simulations, data, or literature is the missing layer.
- **Which bridges matter**: transferability scoring approximates it, but determining whether a bridge produces *new science* needs real-world validation.
- **Scale**: competing-hypothesis maintenance is more expensive than point estimation. The cost/benefit at scale is unmeasured.
- **Adversarial robustness**: a system that maintains alternatives is harder to fool with a single misleading input — but this is hypothesized, not demonstrated.
