# The Commons v0.6 five-world pilot — implementation-failure postmortem

## Status

The engineering pilot is **invalid for scientific interpretation**.

The frozen run made its 30 authorized Generation Two model calls. Every
`Runner.run` returned and its final output passed the `ChildRevision` type check.
The implementation then failed while attempting to serialize an optional SDK
`new_items` structure containing the Pydantic `ChildRevision` class.

The common exception was:

```text
TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
```

The traceback places the failure after `call_trial()` returned, in
`to_jsonable(result.new_items)`. Because the parsed output, usage object, raw
responses, and optional SDK objects were assembled in one dictionary expression,
the exception prevented the essential parsed output and usage from being written.

## What was preserved

- the five frozen worlds and randomized 30-trial order;
- all 30 rendered prompts;
- the passing pre-API validation artifacts;
- the exact executed script hash;
- a run-state record containing 30 attempts;
- 30 per-trial error records containing the rendered instructions/prompt and
  complete local traceback;
- the automatically generated failure report and results JSON.

## What was not preserved

- parsed `ChildRevision` values returned by the model;
- raw SDK/API response objects;
- response IDs;
- per-trial token usage;
- aggregate token usage.

The generated `pilot_report.md` says the SDK reported zero requests and zero
tokens. That is a consequence of usage not being committed after the serializer
failed; it is **not** evidence that no model calls occurred.

## Call accounting

- Frozen authorization: 30 logical model calls.
- Attempt records: 30.
- Calls that returned past `Runner.run` and the structured-output type check: 30.
- Additional calls or retries after diagnosis: 0.
- Generation Three calls: 0.
- Main-experiment calls: 0.

Transport-level retry counts and billed token counts cannot be reconstructed
from the local artifacts.

## Consequence

There are no usable pilot condition results. Valid, Masked, and Shuffled cannot
be compared, and this run provides no evidence for or against a provenance
effect. The design is **not ready for the main run** because the output-preservation
path failed its engineering purpose.

No pilot trial will be repeated without a new explicit authorization. The failed
run and its artifacts should remain immutable.

## Required implementation repair before any new run

1. Serialize Python/Pydantic classes as class identifiers rather than calling
   instance methods on them.
2. Commit the parsed final output, scoring, and usage before attempting to
   serialize optional SDK internals.
3. Make optional serialization failure non-fatal and record it separately.
4. Add a local serializer regression test containing a dataclass whose field is
   the `ChildRevision` class.
5. Use a new run directory and authorization for any replacement pilot so this
   failed run is not overwritten.

## Integrity identifiers

- Executed `the_commons_v0_6.py` SHA-256:
  `1a4ea925d581a62984e6f8fde67bda4c7bea4c9f78d17d6d8fe17d0fe041d01e`
- Frozen worlds SHA-256:
  `aa5d8bed3448d11924321012d4eca3518acfe55011038e03e31c24fede49e5c9`
- Validation JSON SHA-256:
  `c2039915a9d1600426b2b856fb73c11ffc05b07a036771b7ac4b074d9d4356bf`

Run interval: `2026-08-16T04:21:54.579671+00:00` to
`2026-08-16T04:23:08.706223+00:00`.
