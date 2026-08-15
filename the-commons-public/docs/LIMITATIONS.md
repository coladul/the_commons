# Limitations and reasons for caution

This project is intentionally described as an exploratory prototype.

## 1. Same underlying model family

All experimental branches in the recorded later versions used the same API model (`gpt-5.6-luna`). Fresh calls do not imply independent training histories or architectures.

## 2. Synthetic worlds

The objective grader is a strength, but the worlds are artificial. v0.5 varies thresholds while keeping the same broad two-threshold hypothesis class. A result that is stable here may fail on richer causal graphs, noisy observations, natural-language evidence, real scientific literature, or adversarial data.

## 3. Adaptive experiment sequence

v0.2–v0.5 were designed sequentially after seeing earlier results. The work was not preregistered. v0.5 is a replication *inside the project*, not an independent preregistered replication.

## 4. Small number of worlds

v0.5 uses 10 worlds. Bootstrap intervals describe variation among those worlds; they do not establish external validity.

## 5. Generated false ancestors are systematic

The v0.5 false ancestral thresholds are generated from the true thresholds by fixed offsets. Other forms of misinformation may behave very differently.

## 6. The prompt defines the hypothesis class

Children are told the rule has one temperature comparison, one density comparison, and AND/OR logic. This greatly constrains inference. It is useful for objective scoring, but limits generalization.

## 7. Evidence design can be ambiguous

Finite observation sets can support multiple rules that fit every observed case. Several agents confidently inferred wrong rules that happened to fit the sample. This is partly the phenomenon being studied, but it also means conclusions depend on the experimental evidence design.

## 8. Model stochasticity and service changes

Exact API outputs may not reproduce. Served model behavior may change over time, and the original environment did not fully pin dependency versions.

## 9. No independent human replication yet

The same human/AI collaboration designed the experiment, executed it, and interpreted it. Outside reviewers have not yet independently rerun the code.

## 10. No consciousness inference

The words "ancestor," "child," "grandchild," "culture," and "inheritance" describe information flow in an experimental architecture. They do not establish subjective lineage, awareness, or autobiographical memory.

## 11. Provenance is not magic

In v0.5, some False Claim + Provenance branches still made obvious logical mistakes despite having sufficient evidence. The correct engineering lesson is not "provenance solves misinformation." It is closer to "provenance can make correction possible and sometimes improves it, but verification is still needed."

## 12. Multiple comparisons / exploratory interpretation

Several contrasts and descriptive outcomes are examined. The reported intervals are useful summaries, not a license to select whichever comparison looks most dramatic.

## 13. Archive-assessment schema artifact

In v0.5, `Evidence Only` contains no ancestral interpretive claim, yet the structured output still requires an `archive_assessment` value and the model sometimes labels the evidence "accepted" or "revised." Those labels should not be interpreted psychologically or methodologically; they are a schema-design artifact and should be removed or redefined in a future version.
