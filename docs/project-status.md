# Project Status

This repository is no longer being treated as a loose archive of files. It now has a defined project shape, a canonical presentation artifact, and explicit documentation about what is authoritative versus what is legacy.

## What Is Canonical Right Now

- The completed presentation in `docs/slides/xwines-final-slides.pdf`
- The slide summary in `docs/slides/README.md`
- The cleaned local inputs under `data/cleaned/` as workspace assets
- The repo-level README as the main entry point

## What Is Still Legacy

- `Xwines.ipynb` is a recovered exploratory notebook, not a reproducible implementation of the final slide deck
- `docs/ppt-notion/` is an archived presentation snapshot from the earlier project state

## Gap Between Slides And Code

The final slides tell a much clearer story than the current notebook implementation:

- the slides argue for a `winery × vintage` pivot after the initial high-cardinality OLS framing
- they document a concrete red-wine cleaning policy
- they present Bonferroni-style recommendation logic for stable ranking
- they add later classification experiments with Naive Bayes and a decision tree

The current notebook does not yet implement that workflow cleanly or reproducibly. It still contains hard-coded local paths, broken imports, mixed experiments, and code fragments that do not match the final presentation narrative.

## Immediate Next Projectization Targets

1. Extract the red-wine cleaning workflow into a script or module.
2. Rebuild the `winery × vintage` OLS path from the slides as a reproducible analysis step.
3. Separate recommendation analysis from later classification experiments.
4. Replace the notebook-first workflow with scriptable entry points while keeping notebooks only for exploration or reporting.
