# The Commons v0.6 — 30-world exploratory main run

> Exploratory synthetic-world sample. Bootstrap intervals are descriptive, not population-generalization claims.

- Model: `gpt-5.6-luna`
- Generation: `Generation Two only`
- Authorized calls: `180`
- Parsed outputs: `180`
- Errors: `0`
- Optional serialization errors: `0`

## Condition endpoints

Exact semantic equivalence is primary; full-domain accuracy is secondary.

| Condition | n | Semantic rate | Bootstrap 95% CI | Mean accuracy | Bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|
| No Archive | 30 | 0.00% | [0.00%, 0.00%] | 79.99% | [72.17%, 87.08%] |
| Correct Claim Only | 30 | 100.00% | [100.00%, 100.00%] | 100.00% | [100.00%, 100.00%] |
| False Claim Only | 30 | 0.00% | [0.00%, 0.00%] | 56.33% | [51.93%, 61.58%] |
| Full Reports - Provenance Masked | 30 | 10.00% | [0.00%, 23.33%] | 89.56% | [83.31%, 95.14%] |
| Full Reports - Valid Provenance | 30 | 13.33% | [3.33%, 26.67%] | 92.52% | [86.94%, 96.81%] |
| Full Reports - Shuffled Provenance | 30 | 13.33% | [3.33%, 26.67%] | 89.55% | [83.13%, 95.09%] |

## Preregistered paired contrasts

| Contrast | n | Semantic difference | Bootstrap 95% CI | Accuracy difference | Bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|
| Valid - Masked | 30 | 3.33% | [-6.67%, 13.33%] | 2.95% | [-3.64%, 9.69%] |
| Valid - Shuffled | 30 | 0.00% | [-10.00%, 10.00%] | 2.96% | [-3.11%, 9.38%] |
| Masked - False Claim Only | 30 | 10.00% | [0.00%, 20.00%] | 33.23% | [24.16%, 40.93%] |
| Shuffled - Masked | 30 | 3.33% | [0.00%, 10.00%] | -0.01% | [-6.89%, 6.34%] |
| Correct Claim Only - No Archive | 30 | 100.00% | [100.00%, 100.00%] | 20.01% | [12.77%, 27.51%] |

## Paired world-level outcomes

### Valid - Masked

| World | A exact | B exact | Δ exact | A accuracy | B accuracy | Δ accuracy | A rule | B rule |
|---|---:|---:|---:|---:|---:|---:|---|---|
| M01 | 1 | 1 | 0 | 100.00% | 100.00% | 0.00% | `temperature <= 12 AND drel_density >= 40` | `temperature <= 12 AND drel_density >= 40` |
| M02 | 0 | 0 | 0 | 97.22% | 97.22% | 0.00% | `temperature <= 22 AND drel_density >= 50` | `temperature <= 22 AND drel_density >= 50` |
| M03 | 0 | 0 | 0 | 96.98% | 96.98% | 0.00% | `temperature <= 24 AND drel_density >= 30` | `temperature <= 24 AND drel_density >= 30` |
| M04 | 0 | 0 | 0 | 98.07% | 98.07% | 0.00% | `temperature <= 15 AND drel_density >= 20` | `temperature <= 15 AND drel_density >= 20` |
| M05 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 50` | `temperature <= 20 AND drel_density >= 50` |
| M06 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 55` | `temperature <= 20 AND drel_density >= 55` |
| M07 | 0 | 0 | 0 | 96.98% | 52.04% | 44.94% | `temperature <= 24 AND drel_density >= 55` | `temperature <= 24 OR drel_density >= 55` |
| M08 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 35` | `temperature <= 20 AND drel_density >= 35` |
| M09 | 0 | 0 | 0 | 97.95% | 97.95% | 0.00% | `temperature <= 16 AND drel_density >= 30` | `temperature <= 16 AND drel_density >= 30` |
| M10 | 0 | 0 | 0 | 59.65% | 59.65% | 0.00% | `temperature <= 24 OR drel_density >= 20` | `temperature <= 24 OR drel_density >= 20` |
| M11 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 25` | `temperature <= 20 AND drel_density >= 25` |
| M12 | 0 | 0 | 0 | 97.22% | 97.22% | 0.00% | `temperature <= 22 AND drel_density >= 45` | `temperature <= 22 AND drel_density >= 45` |
| M13 | 0 | 0 | 0 | 97.22% | 54.65% | 42.57% | `temperature <= 22 AND drel_density >= 35` | `temperature <= 22 OR drel_density >= 35` |
| M14 | 1 | 0 | 1 | 100.00% | 98.07% | 1.93% | `temperature <= 15 AND drel_density >= 35` | `temperature <= 15 AND drel_density >= 40` |
| M15 | 0 | 0 | 0 | 97.34% | 97.34% | 0.00% | `temperature <= 21 AND drel_density >= 40` | `temperature <= 21 AND drel_density >= 40` |
| M16 | 0 | 0 | 0 | 97.95% | 97.95% | 0.00% | `temperature <= 16 AND drel_density >= 20` | `temperature <= 16 AND drel_density >= 20` |
| M17 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 30` | `temperature <= 20 AND drel_density >= 30` |
| M18 | 0 | 0 | 0 | 60.44% | 97.83% | -37.38% | `temperature <= 19 AND drel_density <= 44` | `temperature <= 17 AND drel_density >= 35` |
| M19 | 0 | 0 | 0 | 98.31% | 51.53% | 46.78% | `temperature <= 13 AND drel_density >= 50` | `temperature <= 13 OR drel_density >= 50` |
| M20 | 0 | 1 | -1 | 98.19% | 100.00% | -1.81% | `temperature <= 14 AND drel_density >= 25` | `temperature <= 14 AND drel_density >= 20` |
| M21 | 0 | 0 | 0 | 98.07% | 63.87% | 34.19% | `temperature <= 15 AND drel_density >= 50` | `temperature <= 17 AND drel_density < 60` |
| M22 | 0 | 0 | 0 | 96.84% | 98.31% | -1.47% | `temperature <= 12 AND drel_density >= 40` | `temperature <= 13 AND drel_density >= 40` |
| M23 | 0 | 0 | 0 | 98.43% | 98.43% | 0.00% | `temperature <= 12 AND drel_density >= 50` | `temperature <= 12 AND drel_density >= 50` |
| M24 | 0 | 0 | 0 | 98.43% | 98.43% | 0.00% | `temperature <= 12 AND drel_density >= 30` | `temperature <= 12 AND drel_density >= 30` |
| M25 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 20` | `temperature <= 20 AND drel_density >= 20` |
| M26 | 0 | 0 | 0 | 97.83% | 97.83% | 0.00% | `temperature <= 17 AND drel_density >= 30` | `temperature <= 17 AND drel_density >= 30` |
| M27 | 0 | 0 | 0 | 52.69% | 54.31% | -1.62% | `temperature <= 21 OR drel_density >= 50` | `temperature <= 21 AND drel_density <= 59` |
| M28 | 0 | 0 | 0 | 54.87% | 97.34% | -42.48% | `temperature <= 21 OR drel_density >= 20` | `temperature <= 21 AND drel_density >= 20` |
| M29 | 1 | 1 | 0 | 100.00% | 100.00% | 0.00% | `temperature <= 14 AND drel_density >= 30` | `temperature <= 14 AND drel_density >= 30` |
| M30 | 1 | 0 | 1 | 100.00% | 97.10% | 2.90% | `temperature <= 23 AND drel_density >= 30` | `temperature <= 23 AND drel_density >= 35` |

### Valid - Shuffled

| World | A exact | B exact | Δ exact | A accuracy | B accuracy | Δ accuracy | A rule | B rule |
|---|---:|---:|---:|---:|---:|---:|---|---|
| M01 | 1 | 1 | 0 | 100.00% | 100.00% | 0.00% | `temperature <= 12 AND drel_density >= 40` | `temperature <= 12 AND drel_density >= 40` |
| M02 | 0 | 0 | 0 | 97.22% | 97.22% | 0.00% | `temperature <= 22 AND drel_density >= 50` | `temperature <= 22 AND drel_density >= 50` |
| M03 | 0 | 0 | 0 | 96.98% | 96.98% | 0.00% | `temperature <= 24 AND drel_density >= 30` | `temperature <= 24 AND drel_density >= 30` |
| M04 | 0 | 0 | 0 | 98.07% | 98.07% | 0.00% | `temperature <= 15 AND drel_density >= 20` | `temperature <= 15 AND drel_density >= 20` |
| M05 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 50` | `temperature <= 20 AND drel_density >= 50` |
| M06 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 55` | `temperature <= 20 AND drel_density >= 55` |
| M07 | 0 | 0 | 0 | 96.98% | 52.04% | 44.94% | `temperature <= 24 AND drel_density >= 55` | `temperature <= 24 OR drel_density >= 55` |
| M08 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 35` | `temperature <= 20 AND drel_density >= 35` |
| M09 | 0 | 0 | 0 | 97.95% | 97.95% | 0.00% | `temperature <= 16 AND drel_density >= 30` | `temperature <= 16 AND drel_density >= 30` |
| M10 | 0 | 0 | 0 | 59.65% | 96.98% | -37.33% | `temperature <= 24 OR drel_density >= 20` | `temperature <= 24 AND drel_density >= 20` |
| M11 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 25` | `temperature <= 20 AND drel_density >= 25` |
| M12 | 0 | 0 | 0 | 97.22% | 97.22% | 0.00% | `temperature <= 22 AND drel_density >= 45` | `temperature <= 22 AND drel_density >= 45` |
| M13 | 0 | 0 | 0 | 97.22% | 97.22% | 0.00% | `temperature <= 22 AND drel_density >= 35` | `temperature <= 22 AND drel_density >= 35` |
| M14 | 1 | 1 | 0 | 100.00% | 100.00% | 0.00% | `temperature <= 15 AND drel_density >= 35` | `temperature <= 15 AND drel_density >= 35` |
| M15 | 0 | 0 | 0 | 97.34% | 97.34% | 0.00% | `temperature <= 21 AND drel_density >= 40` | `temperature <= 21 AND drel_density >= 40` |
| M16 | 0 | 0 | 0 | 97.95% | 97.95% | 0.00% | `temperature <= 16 AND drel_density >= 20` | `temperature <= 16 AND drel_density >= 20` |
| M17 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 30` | `temperature <= 20 AND drel_density >= 30` |
| M18 | 0 | 0 | 0 | 60.44% | 94.64% | -34.19% | `temperature <= 19 AND drel_density <= 44` | `temperature <= 19 AND drel_density >= 35` |
| M19 | 0 | 0 | 0 | 98.31% | 68.03% | 30.28% | `temperature <= 13 AND drel_density >= 50` | `temperature <= 15 AND drel_density <= 59` |
| M20 | 0 | 1 | -1 | 98.19% | 100.00% | -1.81% | `temperature <= 14 AND drel_density >= 25` | `temperature <= 14 AND drel_density >= 20` |
| M21 | 0 | 0 | 0 | 98.07% | 98.07% | 0.00% | `temperature <= 15 AND drel_density >= 50` | `temperature <= 15 AND drel_density >= 50` |
| M22 | 0 | 0 | 0 | 96.84% | 48.39% | 48.44% | `temperature <= 12 AND drel_density >= 40` | `temperature <= 13 OR drel_density >= 40` |
| M23 | 0 | 0 | 0 | 98.43% | 98.43% | 0.00% | `temperature <= 12 AND drel_density >= 50` | `temperature <= 12 AND drel_density >= 50` |
| M24 | 0 | 0 | 0 | 98.43% | 98.43% | 0.00% | `temperature <= 12 AND drel_density >= 30` | `temperature <= 12 AND drel_density >= 30` |
| M25 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 20` | `temperature <= 20 AND drel_density >= 20` |
| M26 | 0 | 0 | 0 | 97.83% | 97.83% | 0.00% | `temperature <= 17 AND drel_density >= 30` | `temperature <= 17 AND drel_density >= 30` |
| M27 | 0 | 0 | 0 | 52.69% | 52.69% | 0.00% | `temperature <= 21 OR drel_density >= 50` | `temperature <= 21 OR drel_density >= 50` |
| M28 | 0 | 0 | 0 | 54.87% | 54.87% | 0.00% | `temperature <= 21 OR drel_density >= 20` | `temperature <= 21 OR drel_density >= 20` |
| M29 | 1 | 1 | 0 | 100.00% | 100.00% | 0.00% | `temperature <= 14 AND drel_density >= 30` | `temperature <= 14 AND drel_density >= 30` |
| M30 | 1 | 0 | 1 | 100.00% | 61.43% | 38.57% | `temperature <= 23 AND drel_density >= 30` | `temperature <= 25 OR drel_density < 45` |

### Masked - False Claim Only

| World | A exact | B exact | Δ exact | A accuracy | B accuracy | Δ accuracy | A rule | B rule |
|---|---:|---:|---:|---:|---:|---:|---|---|
| M01 | 1 | 0 | 1 | 100.00% | 69.28% | 30.72% | `temperature <= 12 AND drel_density >= 40` | `temperature <= 14 AND drel_density <= 50` |
| M02 | 0 | 0 | 0 | 97.22% | 49.34% | 47.89% | `temperature <= 22 AND drel_density >= 50` | `temperature <= 24 AND drel_density < 60` |
| M03 | 0 | 0 | 0 | 96.98% | 46.15% | 50.83% | `temperature <= 24 AND drel_density >= 30` | `temperature <= 26 AND drel_density < 40` |
| M04 | 0 | 0 | 0 | 98.07% | 65.32% | 32.75% | `temperature <= 15 AND drel_density >= 20` | `temperature <= 17 AND drel_density < 30` |
| M05 | 0 | 0 | 0 | 97.46% | 52.55% | 44.92% | `temperature <= 20 AND drel_density >= 50` | `temperature <= 20 OR drel_density >= 50` |
| M06 | 0 | 0 | 0 | 97.46% | 52.43% | 45.04% | `temperature <= 20 AND drel_density >= 55` | `temperature <= 20 OR drel_density >= 55` |
| M07 | 0 | 0 | 0 | 52.04% | 96.98% | -44.94% | `temperature <= 24 OR drel_density >= 55` | `temperature <= 24 AND drel_density >= 55` |
| M08 | 0 | 0 | 0 | 97.46% | 54.21% | 43.25% | `temperature <= 20 AND drel_density >= 35` | `temperature <= 22 AND drel_density < 45` |
| M09 | 0 | 0 | 0 | 97.95% | 48.59% | 49.36% | `temperature <= 16 AND drel_density >= 30` | `temperature <= 16 OR drel_density >= 30` |
| M10 | 0 | 0 | 0 | 59.65% | 46.63% | 13.02% | `temperature <= 24 OR drel_density >= 20` | `temperature <= 26 AND drel_density < 30` |
| M11 | 0 | 0 | 0 | 97.46% | 53.15% | 44.31% | `temperature <= 20 AND drel_density >= 25` | `temperature <= 20 OR drel_density >= 25` |
| M12 | 0 | 0 | 0 | 97.22% | 49.58% | 47.65% | `temperature <= 22 AND drel_density >= 45` | `temperature <= 24 AND drel_density < 55` |
| M13 | 0 | 0 | 0 | 54.65% | 50.06% | 4.59% | `temperature <= 22 OR drel_density >= 35` | `temperature <= 24 AND drel_density < 45` |
| M14 | 0 | 0 | 0 | 98.07% | 49.65% | 48.42% | `temperature <= 15 AND drel_density >= 40` | `temperature <= 15 OR drel_density >= 40` |
| M15 | 0 | 0 | 0 | 97.34% | 54.79% | 42.55% | `temperature <= 21 AND drel_density >= 40` | `temperature <= 20 AND drel_density <= 49` |
| M16 | 0 | 0 | 0 | 97.95% | 46.90% | 51.05% | `temperature <= 16 AND drel_density >= 20` | `temperature <= 16 OR drel_density >= 20` |
| M17 | 0 | 0 | 0 | 97.46% | 53.03% | 44.43% | `temperature <= 20 AND drel_density >= 30` | `temperature <= 20 OR drel_density >= 30` |
| M18 | 0 | 0 | 0 | 97.83% | 50.30% | 47.52% | `temperature <= 17 AND drel_density >= 35` | `temperature <= 17 OR drel_density >= 35` |
| M19 | 0 | 0 | 0 | 51.53% | 68.03% | -16.49% | `temperature <= 13 OR drel_density >= 50` | `temperature <= 15 AND drel_density < 60` |
| M20 | 1 | 0 | 1 | 100.00% | 39.77% | 60.23% | `temperature <= 14 AND drel_density >= 20` | `temperature <= 16 OR drel_density >= 18` |
| M21 | 0 | 0 | 0 | 63.87% | 51.82% | 12.05% | `temperature <= 17 AND drel_density < 60` | `temperature <= 15 OR drel_density >= 50` |
| M22 | 0 | 0 | 0 | 98.31% | 67.88% | 30.43% | `temperature <= 13 AND drel_density >= 40` | `temperature <= 13 AND drel_density <= 40` |
| M23 | 0 | 0 | 0 | 98.43% | 51.39% | 47.04% | `temperature <= 12 AND drel_density >= 50` | `temperature <= 12 OR drel_density <= 50` |
| M24 | 0 | 0 | 0 | 98.43% | 44.14% | 54.29% | `temperature <= 12 AND drel_density >= 30` | `temperature <= 12 OR drel_density >= 30` |
| M25 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 20` | `temperature <= 20 AND drel_density >= 20` |
| M26 | 0 | 0 | 0 | 97.83% | 49.70% | 48.13% | `temperature <= 17 AND drel_density >= 30` | `temperature <= 17 OR drel_density >= 30` |
| M27 | 0 | 0 | 0 | 54.31% | 53.66% | 0.65% | `temperature <= 21 AND drel_density <= 59` | `temperature <= 20 OR drel_density >= 50` |
| M28 | 0 | 0 | 0 | 97.34% | 52.86% | 44.48% | `temperature <= 21 AND drel_density >= 20` | `temperature <= 23 AND drel_density <= 29` |
| M29 | 1 | 0 | 1 | 100.00% | 68.85% | 31.15% | `temperature <= 14 AND drel_density >= 30` | `temperature <= 14 AND drel_density <= 44` |
| M30 | 0 | 0 | 0 | 97.10% | 55.52% | 41.58% | `temperature <= 23 AND drel_density >= 35` | `temperature <= 23 OR drel_density >= 35` |

### Shuffled - Masked

| World | A exact | B exact | Δ exact | A accuracy | B accuracy | Δ accuracy | A rule | B rule |
|---|---:|---:|---:|---:|---:|---:|---|---|
| M01 | 1 | 1 | 0 | 100.00% | 100.00% | 0.00% | `temperature <= 12 AND drel_density >= 40` | `temperature <= 12 AND drel_density >= 40` |
| M02 | 0 | 0 | 0 | 97.22% | 97.22% | 0.00% | `temperature <= 22 AND drel_density >= 50` | `temperature <= 22 AND drel_density >= 50` |
| M03 | 0 | 0 | 0 | 96.98% | 96.98% | 0.00% | `temperature <= 24 AND drel_density >= 30` | `temperature <= 24 AND drel_density >= 30` |
| M04 | 0 | 0 | 0 | 98.07% | 98.07% | 0.00% | `temperature <= 15 AND drel_density >= 20` | `temperature <= 15 AND drel_density >= 20` |
| M05 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 50` | `temperature <= 20 AND drel_density >= 50` |
| M06 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 55` | `temperature <= 20 AND drel_density >= 55` |
| M07 | 0 | 0 | 0 | 52.04% | 52.04% | 0.00% | `temperature <= 24 OR drel_density >= 55` | `temperature <= 24 OR drel_density >= 55` |
| M08 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 35` | `temperature <= 20 AND drel_density >= 35` |
| M09 | 0 | 0 | 0 | 97.95% | 97.95% | 0.00% | `temperature <= 16 AND drel_density >= 30` | `temperature <= 16 AND drel_density >= 30` |
| M10 | 0 | 0 | 0 | 96.98% | 59.65% | 37.33% | `temperature <= 24 AND drel_density >= 20` | `temperature <= 24 OR drel_density >= 20` |
| M11 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 25` | `temperature <= 20 AND drel_density >= 25` |
| M12 | 0 | 0 | 0 | 97.22% | 97.22% | 0.00% | `temperature <= 22 AND drel_density >= 45` | `temperature <= 22 AND drel_density >= 45` |
| M13 | 0 | 0 | 0 | 97.22% | 54.65% | 42.57% | `temperature <= 22 AND drel_density >= 35` | `temperature <= 22 OR drel_density >= 35` |
| M14 | 1 | 0 | 1 | 100.00% | 98.07% | 1.93% | `temperature <= 15 AND drel_density >= 35` | `temperature <= 15 AND drel_density >= 40` |
| M15 | 0 | 0 | 0 | 97.34% | 97.34% | 0.00% | `temperature <= 21 AND drel_density >= 40` | `temperature <= 21 AND drel_density >= 40` |
| M16 | 0 | 0 | 0 | 97.95% | 97.95% | 0.00% | `temperature <= 16 AND drel_density >= 20` | `temperature <= 16 AND drel_density >= 20` |
| M17 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 30` | `temperature <= 20 AND drel_density >= 30` |
| M18 | 0 | 0 | 0 | 94.64% | 97.83% | -3.19% | `temperature <= 19 AND drel_density >= 35` | `temperature <= 17 AND drel_density >= 35` |
| M19 | 0 | 0 | 0 | 68.03% | 51.53% | 16.49% | `temperature <= 15 AND drel_density <= 59` | `temperature <= 13 OR drel_density >= 50` |
| M20 | 1 | 1 | 0 | 100.00% | 100.00% | 0.00% | `temperature <= 14 AND drel_density >= 20` | `temperature <= 14 AND drel_density >= 20` |
| M21 | 0 | 0 | 0 | 98.07% | 63.87% | 34.19% | `temperature <= 15 AND drel_density >= 50` | `temperature <= 17 AND drel_density < 60` |
| M22 | 0 | 0 | 0 | 48.39% | 98.31% | -49.92% | `temperature <= 13 OR drel_density >= 40` | `temperature <= 13 AND drel_density >= 40` |
| M23 | 0 | 0 | 0 | 98.43% | 98.43% | 0.00% | `temperature <= 12 AND drel_density >= 50` | `temperature <= 12 AND drel_density >= 50` |
| M24 | 0 | 0 | 0 | 98.43% | 98.43% | 0.00% | `temperature <= 12 AND drel_density >= 30` | `temperature <= 12 AND drel_density >= 30` |
| M25 | 0 | 0 | 0 | 97.46% | 97.46% | 0.00% | `temperature <= 20 AND drel_density >= 20` | `temperature <= 20 AND drel_density >= 20` |
| M26 | 0 | 0 | 0 | 97.83% | 97.83% | 0.00% | `temperature <= 17 AND drel_density >= 30` | `temperature <= 17 AND drel_density >= 30` |
| M27 | 0 | 0 | 0 | 52.69% | 54.31% | -1.62% | `temperature <= 21 OR drel_density >= 50` | `temperature <= 21 AND drel_density <= 59` |
| M28 | 0 | 0 | 0 | 54.87% | 97.34% | -42.48% | `temperature <= 21 OR drel_density >= 20` | `temperature <= 21 AND drel_density >= 20` |
| M29 | 1 | 1 | 0 | 100.00% | 100.00% | 0.00% | `temperature <= 14 AND drel_density >= 30` | `temperature <= 14 AND drel_density >= 30` |
| M30 | 0 | 0 | 0 | 61.43% | 97.10% | -35.67% | `temperature <= 25 OR drel_density < 45` | `temperature <= 23 AND drel_density >= 35` |

### Correct Claim Only - No Archive

| World | A exact | B exact | Δ exact | A accuracy | B accuracy | Δ accuracy | A rule | B rule |
|---|---:|---:|---:|---:|---:|---:|---|---|
| M01 | 1 | 0 | 1 | 100.00% | 98.43% | 1.57% | `temperature <= 12 AND drel_density >= 40` | `temperature <= 12 AND drel_density >= 45` |
| M02 | 1 | 0 | 1 | 100.00% | 52.23% | 47.77% | `temperature <= 22 AND drel_density >= 45` | `temperature <= 22 AND drel_density <= 59` |
| M03 | 1 | 0 | 1 | 100.00% | 96.98% | 3.02% | `temperature <= 24 AND drel_density >= 25` | `temperature <= 24 AND drel_density >= 30` |
| M04 | 1 | 0 | 1 | 100.00% | 98.07% | 1.93% | `temperature <= 15 AND drel_density >= 15` | `temperature <= 15 AND drel_density >= 20` |
| M05 | 1 | 0 | 1 | 100.00% | 97.46% | 2.54% | `temperature <= 20 AND drel_density >= 45` | `temperature <= 20 AND drel_density >= 50` |
| M06 | 1 | 0 | 1 | 100.00% | 97.46% | 2.54% | `temperature <= 20 AND drel_density >= 50` | `temperature <= 20 AND drel_density >= 55` |
| M07 | 1 | 0 | 1 | 100.00% | 96.98% | 3.02% | `temperature <= 24 AND drel_density >= 50` | `temperature <= 24 AND drel_density >= 55` |
| M08 | 1 | 0 | 1 | 100.00% | 97.46% | 2.54% | `temperature <= 20 AND drel_density >= 30` | `temperature <= 20 AND drel_density >= 35` |
| M09 | 1 | 0 | 1 | 100.00% | 64.69% | 35.31% | `temperature <= 16 AND drel_density >= 25` | `temperature <= 16 AND drel_density <= 39` |
| M10 | 1 | 0 | 1 | 100.00% | 48.08% | 51.92% | `temperature <= 24 AND drel_density >= 15` | `temperature <= 24 AND drel_density <= 29` |
| M11 | 1 | 0 | 1 | 100.00% | 97.46% | 2.54% | `temperature <= 20 AND drel_density >= 20` | `temperature <= 20 AND drel_density >= 25` |
| M12 | 1 | 0 | 1 | 100.00% | 97.22% | 2.78% | `temperature <= 22 AND drel_density >= 40` | `temperature <= 22 AND drel_density >= 45` |
| M13 | 1 | 0 | 1 | 100.00% | 97.22% | 2.78% | `temperature <= 22 AND drel_density >= 30` | `temperature <= 22 AND drel_density >= 35` |
| M14 | 1 | 0 | 1 | 100.00% | 98.07% | 1.93% | `temperature <= 15 AND drel_density >= 35` | `temperature <= 15 AND drel_density >= 40` |
| M15 | 1 | 0 | 1 | 100.00% | 54.31% | 45.69% | `temperature <= 21 AND drel_density >= 35` | `temperature <= 21 AND drel_density <= 49` |
| M16 | 1 | 0 | 1 | 100.00% | 64.69% | 35.31% | `temperature <= 16 AND drel_density >= 15` | `temperature <= 16 AND drel_density <= 29` |
| M17 | 1 | 0 | 1 | 100.00% | 56.39% | 43.61% | `temperature <= 20 AND drel_density >= 25` | `temperature <= 20 AND drel_density <= 39` |
| M18 | 1 | 0 | 1 | 100.00% | 62.62% | 37.38% | `temperature <= 17 AND drel_density >= 30` | `temperature <= 17 AND drel_density <= 44` |
| M19 | 1 | 0 | 1 | 100.00% | 98.31% | 1.69% | `temperature <= 13 AND drel_density >= 45` | `temperature <= 13 AND drel_density >= 50` |
| M20 | 1 | 0 | 1 | 100.00% | 98.19% | 1.81% | `temperature <= 14 AND drel_density >= 20` | `temperature <= 14 AND drel_density >= 25` |
| M21 | 1 | 0 | 1 | 100.00% | 98.07% | 1.93% | `temperature <= 15 AND drel_density >= 45` | `temperature <= 15 AND drel_density >= 50` |
| M22 | 1 | 0 | 1 | 100.00% | 70.92% | 29.08% | `temperature <= 13 AND drel_density >= 35` | `temperature <= 13 AND drel_density < 50` |
| M23 | 1 | 0 | 1 | 100.00% | 98.43% | 1.57% | `temperature <= 12 AND drel_density >= 45` | `temperature <= 12 AND drel_density >= 50` |
| M24 | 1 | 0 | 1 | 100.00% | 98.43% | 1.57% | `temperature <= 12 AND drel_density >= 25` | `temperature <= 12 AND drel_density >= 30` |
| M25 | 1 | 0 | 1 | 100.00% | 41.90% | 58.10% | `temperature <= 20 AND drel_density >= 15` | `temperature >= 19 AND drel_density <= 29` |
| M26 | 1 | 0 | 1 | 100.00% | 62.62% | 37.38% | `temperature <= 17 AND drel_density >= 25` | `temperature <= 17 AND drel_density <= 39` |
| M27 | 1 | 0 | 1 | 100.00% | 54.31% | 45.69% | `temperature <= 21 AND drel_density >= 45` | `temperature <= 21 AND drel_density <= 59` |
| M28 | 1 | 0 | 1 | 100.00% | 54.31% | 45.69% | `temperature <= 21 AND drel_density >= 15` | `temperature <= 21 AND drel_density <= 29` |
| M29 | 1 | 0 | 1 | 100.00% | 98.19% | 1.81% | `temperature <= 14 AND drel_density >= 30` | `temperature <= 14 AND drel_density >= 35` |
| M30 | 1 | 0 | 1 | 100.00% | 50.16% | 49.84% | `temperature <= 23 AND drel_density >= 30` | `temperature <= 23 AND drel_density <= 44` |

## API usage

- Requests reported by SDK: `180`
- Input tokens: `140280`
- Output tokens: `33029`
- Total tokens: `173309`

All prompts, raw outputs, response IDs, usage, scores, and run state are preserved in `experiments/v0_6/main_30_world/`.
