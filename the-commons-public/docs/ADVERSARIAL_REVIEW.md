# Adversarial review guide

Please approach this project as if its authors are unintentionally fooling themselves.

The goal is not to be polite to the hypothesis. The goal is to find the strongest alternative explanation.

## Questions for a reviewer

1. **Prompt artifacts:** Do the archive conditions differ in ways other than the intended informational manipulation?
2. **Evidence leakage:** Does any condition accidentally reveal the hidden rule through wording, examples, threshold construction, or formatting?
3. **Generator bias:** Does the fixed relationship between true and false thresholds make one correction strategy unusually easy?
4. **Hypothesis-class bias:** Does telling agents the exact structural form of the rule make the result trivial or distort the effect of inheritance?
5. **Scoring:** Is full-domain accuracy the right metric? Does the distribution of true/false states make high accuracy misleading?
6. **Semantic equivalence:** Is exhaustive equality over the defined integer domain implemented correctly?
7. **Grandchild tests:** Are the 24 scenarios sufficiently diagnostic, balanced, and independent of the parent-generation evidence?
8. **Statistics:** Are the bootstrap intervals and paired contrasts appropriate for 10 generated worlds? What would be a better confirmatory analysis?
9. **Model dependence:** Would the result persist across different models, temperatures, providers, or prompt formulations?
10. **Interpretation:** Is "anchoring" the best description, or is there a simpler prompt-conditioning explanation?
11. **Provenance confound:** Is the benefit from provenance actually due to more tokens, repeated boundary examples, or stronger evidence density rather than provenance as a concept?
12. **Evidence-only condition:** Why did some Evidence Only branches produce reversed inequalities despite claiming all observations fit? Does this expose a task-design flaw?
13. **Adaptive research:** Which claims should be treated as exploratory because they were formulated after seeing earlier runs?
14. **Reproducibility:** What information is missing that an outside researcher would need for a serious replication?

## Suggested AI-review prompt

Copy the following into a fresh model without telling it that the authors are excited about the project:

> You are an adversarial methodological reviewer. Assume the experimenters may be unintentionally fooling themselves. Read the attached code and reports for The Commons v0.1–v0.5. Identify coding errors, prompt confounds, information leakage, invalid statistical interpretations, weak controls, alternative explanations, and claims that exceed the evidence. Prioritize flaws that could explain the v0.5 condition differences without invoking a meaningful effect of epistemic inheritance. For every criticism, point to the relevant code or report detail and propose a concrete falsification experiment. Do not reward novelty or narrative appeal.

## Best possible outcome

A fatal flaw is useful. A failed replication is useful. A narrower interpretation is useful.

The project should improve by surviving criticism, not by avoiding it.
