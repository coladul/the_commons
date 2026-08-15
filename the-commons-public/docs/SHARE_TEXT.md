# Drafts for sharing The Commons

## Short public post

I built a small experimental project with ChatGPT called **The Commons**. It tests whether discoveries and mistakes produced by one set of LLM agents can be preserved in an external shared record and affect later fresh agents.

The interesting result so far is not about consciousness. In a 10-world synthetic replication, agents given a confident false ancestral claim performed worse than agents with no archive, while preserving the evidence behind the false claim substantially improved downstream grandchild performance. The repo includes the code, null/failed versions, exact reports, limitations, and an adversarial-review checklist.

I would genuinely like people to try to break it. What confounds or design errors are we missing?

[REPOSITORY LINK]

## More technical post

**The Commons: experiments in epistemic inheritance between LLM agents**

I am sharing an exploratory multi-agent framework that studies external knowledge inheritance rather than subjective memory. v0.3 showed model-generated novel information improving fresh-agent accuracy in an objectively graded fictional world. v0.4 introduced a false ancestor and multi-generational correction. v0.5 repeated the design across 10 generated threshold worlds with paired conditions and exhaustive semantic-equivalence grading.

In the recorded v0.5 run, False Claim Only underperformed No Archive by 16.8 percentage points in Generation Two (bootstrap 95% CI −31.1 to −1.9). False Claim + Provenance outperformed False Claim Only by 24.2 points in Generation Three (CI +13.3 to +33.3). Provenance did not clearly outperform Evidence Only.

This is exploratory, same-model, synthetic-world work—not a consciousness claim or a general result about all LLMs. Code, exact reports, failed/null versions, and limitations are included. Adversarial replication is welcome.

[REPOSITORY LINK]

## Email to a researcher

Subject: Small open experiment on provenance and inherited misinformation in LLM agents

Hello,

I am sharing a small exploratory project called **The Commons** that was co-developed with ChatGPT. It studies whether model-generated knowledge and errors can propagate between fresh LLM instances through an external provenance-preserving archive.

The project evolved through several versions, including a null/ceiling-effect control, objectively graded synthetic-world transfer, a false-ancestor experiment, and a 10-world replication. The current result suggests that a bare false ancestral claim can impair later inference in this setup, while preserving the underlying evidence can improve downstream correction. The repository explicitly does not make a consciousness claim.

I am not looking for validation so much as methodological criticism. If this overlaps with your interests, I would be grateful for any obvious confounds, related work I missed, or suggestions for a stronger falsification experiment.

Repository: [LINK]

Thank you.

## AI reviewer prompt

> Review this repository adversarially. Assume the experimenters are unintentionally fooling themselves. Focus on code bugs, prompt confounds, leakage, bad controls, invalid statistics, and alternative explanations. Point to specific evidence and design a stronger test that could falsify the claimed v0.5 pattern.
