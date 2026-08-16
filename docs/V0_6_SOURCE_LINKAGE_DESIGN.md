# The Commons v0.6 — Source-Linkage Test

## Status

This is the frozen design for the five-world engineering pilot. It does not
replace or modify v0.1–v0.5.

## Primary question

When a fresh Generation Two agent receives the same unattributed false claim,
the same two conflicting source-report packets, and the same source-calibration
history, does correct packet-to-source linkage improve recovery of the hidden
rule relative to masked or shuffled linkage?

The experiment operationalizes provenance narrowly as a correct mapping between
a report packet and the source whose independently checkable calibration history
is shown. It does not test every possible meaning of provenance.

## Conditions

| Condition | Claim | Reports | Calibration | Packet/source linkage |
|---|---|---|---|---|
| No Archive | none | none | none | n/a |
| Correct Claim Only | correct, unattributed | none | none | n/a |
| False Claim Only | false, unattributed | none | none | n/a |
| Full Reports — Provenance Masked | false, unattributed | both | same | masked |
| Full Reports — Valid Provenance | identical false claim | identical reports | identical | correct |
| Full Reports — Shuffled Provenance | identical false claim | identical reports | identical | swapped |

The false ancestral claim is byte-identical and unattributed in the three core
conditions. Provenance is manipulated only on the two report-packet source-ID
fields. Report contents are claims made by sources; they are not presented as
ground-truth observations.

## Primary outcome and contrasts

The primary outcome is Generation Two semantic equivalence across all 4,141
integer states in the defined domain.

Preregistered pilot contrasts:

1. Valid minus Masked: availability of correct source linkage beyond matched
   report content.
2. Valid minus Shuffled: correct rather than incorrect source linkage.
3. Shuffled minus Masked: harm or benefit from misleading linkage rather than
   absent linkage.
4. Masked minus False Claim Only: benefit of the additional report content when
   source linkage cannot be used.

## Pilot scale

Five frozen worlds × six conditions × one fresh Generation Two call = 30 API
calls. The pilot is an engineering and manipulation-check run, not a powered
confirmatory experiment. No Generation Three calls are included.

## Required pre-run validation

Before any API call, the implementation must save the pilot worlds and rendered
prompts, then verify automatically that the Valid, Masked, and Shuffled prompts
are identical after canonicalizing only the two packet-source fields. It must
also verify the claim, report payloads, calibration table, new evidence, prompt
length, counterbalancing, historical v0.1–v0.5 hashes, and expected linkage
assignments.
