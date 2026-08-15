# Publishing checklist for a nontechnical repository owner

The package is already sanitized of the known local databases and API key. Before publishing, use this checklist anyway.

## Before uploading

Make sure you are uploading the **public package folder**, not your working `the_commons_starter` folder.

The public folder should contain files such as:

- `README.md`
- `the_commons.py`
- `the_commons_v0_2.py` through `the_commons_v0_5.py`
- `reports/`
- `docs/`
- `results/`

It should **not** contain:

- `.env`
- `.venv/`
- `the_commons.db`
- `commons_*.db`
- `memory_*.db`
- your API key

## Suggested GitHub repository

Repository name:

```text
the-commons
```

Description:

```text
Experiments in epistemic inheritance, provenance, and error propagation between fresh language-model agents.
```

Visibility: **Public** if you want outside review.

Because this package already has a README and `.gitignore`, avoid creating conflicting versions when the site offers to initialize those files.

## License decision

This package intentionally does not choose a license for you.

If you want others to freely reuse and modify the code, consider a permissive software license such as MIT or Apache-2.0. If you are unsure, leave the repository unlicensed temporarily and choose later. Do not treat this note as legal advice.

## After publishing

1. Open the repository in a private/incognito browser window and verify that no secret is visible.
2. Read the top of the README as if you had never seen the project.
3. Open the v0.5 report and make sure it renders correctly.
4. Enable Issues if you want reviewers to report flaws publicly.
5. Share the repository using one of the drafts in `docs/SHARE_TEXT.md`.

## Do not oversell it

Avoid headlines such as:

- "We proved AI consciousness"
- "AI created its own civilization"
- "LLMs have real ancestral memory"

Prefer:

- "A toy experiment in shared epistemic memory for LLM agents"
- "Can model-generated errors propagate across fresh AI agents?"
- "Testing provenance and inherited misinformation in a synthetic multi-agent setup"
