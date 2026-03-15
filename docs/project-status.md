# Project Status

This repository is no longer being treated as a loose archive of files. It now has a defined project shape, a canonical presentation artifact, and explicit documentation about what is authoritative versus what is legacy.

## What Is Canonical Right Now

- The recovered script in `Xwines.py`
- The recovered notebook in `Xwines.ipynb`
- The completed presentation in `docs/slides/xwines-final-slides.pdf`
- The slide summary in `docs/slides/README.md`
- The cleaned local inputs under `data/cleaned/` as workspace assets
- The repo-level README as the main entry point

## What Is Still Legacy

- `docs/legacy/Xwines-original.ipynb` is the archived copy of the original broken notebook
- `docs/ppt-notion/` is an archived presentation snapshot from the earlier project state

## Current Alignment

The project now has a notebook and script that mirror the slide structure much more closely:

- the root script can rerun the recovered analysis without Jupyter
- the notebook follows the `winery × vintage` pivot explicitly
- the red-wine cleaning rules are now implemented in reusable project code
- the recommendation ranking and Bonferroni filtering are no longer mixed with unrelated SQLite or Windows-path experiments
- the Naive Bayes and decision-tree sections are isolated as appendices instead of polluting the mainline analysis

## Gap Between Slides And Code

The remaining differences are mostly about fidelity and tuning, not notebook chaos:

- sample mode intentionally lowers the label-count threshold so committed outputs stay runnable
- the recommendation top list is method-aligned, but not guaranteed to be numerically identical to the slide deck
- the appendix classification metrics are now reproducible, but still need tuning if the goal is to get closer to the reported slide values

## Immediate Next Projectization Targets

1. Tune full-mode recommendation settings against the recovered cleaned data until the ranking table is closer to the finished slides.
2. Decide whether the appendix classification sections should target fidelity to the reported slide metrics or prioritize cleaner modeling choices.
3. Promote the current root script into a more reusable package-level CLI if we want long-term maintenance beyond the recovery phase.
4. Document the full-data runtime expectations more explicitly for reruns on large local hardware.
