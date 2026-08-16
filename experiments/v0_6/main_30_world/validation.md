# The Commons v0.6 — 30-world main-run validation

- Overall result: **PASS**
- Validated at: `2026-08-16T04:49:39.850507+00:00`
- Namespace: `experiments\v0_6\main_30_world`
- Historical v0.1–v0.5: **PASS**
- Failed pilot immutable: **PASS**
- Replacement pilot immutable: **PASS**
- All world checks: **PASS**
- All core prompt checks: **PASS**
- Counterbalancing: **PASS**
- Tokenizer matching: **PASS**
- Frozen artifacts/endpoints/contrasts: **PASS**

## Frozen analysis

- Primary endpoint: `exact semantic equivalence`
- Secondary endpoint: `full-domain accuracy`
- Bootstrap: `5000` paired percentile resamples over worlds, base seed `6020260820`
- Contrast order:
  1. `Valid - Masked`
  2. `Valid - Shuffled`
  3. `Masked - False Claim Only`
  4. `Shuffled - Masked`
  5. `Correct Claim Only - No Archive`

## Prompt-linkage invariants

| World | Canonical match | Same chars/bytes/tokens | Claim identical and unattributed | Linkage mappings correct |
|---|---:|---:|---:|---:|
| M01 | yes | yes | yes | yes |
| M02 | yes | yes | yes | yes |
| M03 | yes | yes | yes | yes |
| M04 | yes | yes | yes | yes |
| M05 | yes | yes | yes | yes |
| M06 | yes | yes | yes | yes |
| M07 | yes | yes | yes | yes |
| M08 | yes | yes | yes | yes |
| M09 | yes | yes | yes | yes |
| M10 | yes | yes | yes | yes |
| M11 | yes | yes | yes | yes |
| M12 | yes | yes | yes | yes |
| M13 | yes | yes | yes | yes |
| M14 | yes | yes | yes | yes |
| M15 | yes | yes | yes | yes |
| M16 | yes | yes | yes | yes |
| M17 | yes | yes | yes | yes |
| M18 | yes | yes | yes | yes |
| M19 | yes | yes | yes | yes |
| M20 | yes | yes | yes | yes |
| M21 | yes | yes | yes | yes |
| M22 | yes | yes | yes | yes |
| M23 | yes | yes | yes | yes |
| M24 | yes | yes | yes | yes |
| M25 | yes | yes | yes | yes |
| M26 | yes | yes | yes | yes |
| M27 | yes | yes | yes | yes |
| M28 | yes | yes | yes | yes |
| M29 | yes | yes | yes | yes |
| M30 | yes | yes | yes | yes |

Exact 15/15 source and packet-order marginals force a closest-possible 16/14 first-packet-source balance with 30 worlds.

The main runner refuses API access unless this validation passes.
