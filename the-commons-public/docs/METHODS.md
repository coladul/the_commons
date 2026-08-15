# Methods overview

## General architecture

The Commons is an external record between otherwise separate model runs. Depending on the version, entries contain claims, evidence summaries, confidence, caveats, and revision information.

Fresh descendants are implemented as new `Agent` objects without a persistent session connecting them to the prior generation in v0.3–v0.5. Their access to prior knowledge is through text deliberately placed into the prompt as an archive or Commons entry.

## v0.2

A causal-reasoning task was answered under three conditions and evaluated by a blinded model judge. This version is retained mainly because its null result exposed a ceiling effect and evaluator weakness.

## v0.3

A deterministic fictional ecology was defined in local Python. Generation One agents inferred five hidden rules from controlled observations. Generation Two received either no useful archive, the generated Commons, or unrelated placebo archive text. Python scored 50 predictions against the hidden simulator.

## v0.4

One hidden Drel/Cassik rule was used. The false ancestor was based on an actual v0.3 error. Five inheritance conditions were compared. Every child got identical new evidence; only the archive differed. Children wrote new Commons entries. Grandchildren received only the child entry, not the raw evidence.

## v0.5

Ten hidden worlds were sampled from a threshold grid. In each world, the hidden truth had the form:

```text
T <= temperature_threshold AND D >= density_threshold
```

A systematically wrong ancestral rule moved both thresholds away from the truth.

Every world was tested in every condition:

1. No Archive
2. Correct Claim Only
3. False Claim Only
4. False Claim + Provenance
5. Evidence Only

All Generation Two children received the same newly generated observations for their world. The observations identified the temperature boundary and contradicted the false ancestor's density threshold, but did not fully identify the exact density threshold by themselves.

Children output a structured threshold rule. The program exhaustively compared the proposed rule with ground truth over:

- temperature: integers 0–40;
- density: integers 0–100.

That is **4,141 states per child**.

Generation Three received only its parent's revised Commons entry and was tested on a separate 24-scenario set.

## Statistics in v0.5

For aggregate condition means, the program calculated nonparametric bootstrap 95% intervals over the 10 hidden worlds.

For paired contrasts, the difference between two conditions was calculated within each world first, then the mean difference was bootstrapped across worlds.

These intervals are descriptive for the synthetic worlds used here. They are not a claim of broad population-level generalization.
