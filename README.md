# Grape Wine Rating Inference

This repository is being upgraded from a recovered class-project archive into a proper analysis project. The canonical research narrative now comes from the finished slide deck, and the repo structure has been reorganized so the slides, cleaned data, project status, and legacy materials each have a clear role.

## Core Question

The project asks a practical version of the wine-quality problem:

> How can consumers, importers, and winery operators identify highly rated wines using features that are visible in the market, rather than laboratory-style chemical measurements?

That framing comes directly from the final presentation in [docs/slides/xwines-final-slides.pdf](docs/slides/xwines-final-slides.pdf).

## What The Final Slides Actually Say

The finished deck follows this analysis story:

1. Start with the X-Wines dataset and an OLS-style view of wine rating using observable features such as `Type`, `Acidity`, `Grapes`, `Body`, `Country`, and `Vintage`.
2. Recognize that the feature space becomes too high-dimensional to handle cleanly with naive dummy-variable expansion.
3. Pivot to a `winery × vintage` representation as a practical proxy for winery technique, climate, and other latent wine characteristics.
4. Clean the data by keeping the most recent repeated rating, focusing on red wines first, removing thin `winery × vintage` cells, and averaging repeated ratings at the wine-label level.
5. Use large-scale inference carefully: instead of trusting thousands of raw coefficient tests, apply Bonferroni-style reasoning to build a more defensible recommendation list.
6. Extend the project with later classification experiments using Naive Bayes and a decision tree, while acknowledging that the classification branch is weaker than the recommendation story.

This repo is now organized around that narrative rather than around whatever happened to be left in the old notebook.

## Canonical Artifacts

- Recovered script: [Xwines.py](Xwines.py)
- Recovered notebook: [Xwines.ipynb](Xwines.ipynb)
- Official slides: [docs/slides/xwines-final-slides.pdf](docs/slides/xwines-final-slides.pdf)
- Slides summary: [docs/slides/README.md](docs/slides/README.md)
- Project status and upgrade notes: [docs/project-status.md](docs/project-status.md)
- Cleaned local inputs: [data/README.md](data/README.md)
- Legacy notebook archive: [docs/legacy/Xwines-original.ipynb](docs/legacy/Xwines-original.ipynb)
- Legacy presentation archive: [docs/ppt-notion/README.md](docs/ppt-notion/README.md)

## Repo Structure

```text
.
├── README.md
├── Xwines.py                     # script mirror of the canonical notebook
├── Xwines.ipynb                  # canonical recovered notebook
├── data/
│   ├── README.md
│   └── cleaned/
├── docs/
│   ├── legacy/                   # archived copy of the original broken notebook
│   ├── project-status.md
│   ├── ppt-notion/               # archived Notion-era presentation materials
│   └── slides/                   # canonical finished presentation
├── pyproject.toml
├── scripts/
│   └── project_status.py
├── src/
│   └── wine_rating_inference/
└── tests/
```

## Working With The Repo

Install the optional analysis stack into a local virtual environment when you want to execute the recovered notebook end to end:

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[analysis]'
```

Quick status check:

```bash
python3 scripts/project_status.py
```

Basic test run:

```bash
python3 -m unittest discover -s tests
```

Execute the canonical notebook in place:

```bash
.venv/bin/jupyter nbconvert --to notebook --execute --inplace Xwines.ipynb --ExecutePreprocessor.timeout=0
```

Run the same analysis as a script:

```bash
.venv/bin/python Xwines.py --run-mode sample
```

The package metadata lives in [pyproject.toml](pyproject.toml). Analysis dependencies are declared as an optional extra because the recovered project still needs a proper reproducible pipeline before the heavier data science stack becomes the default developer path.

## Data Policy

- Raw X-Wines source remains reference-only: https://github.com/rogerioxavier/X-Wines
- Recovered cleaned source reference: https://drive.google.com/drive/folders/13xFwEdiwVy-EnBzqgvRaHTjjXiqIAKoK?usp=drive_link
- Canonical local inputs live under `data/cleaned/`
- The recovered cleaned CSV files stay local in the workspace and are not committed to GitHub because they are too large for a normal source repository

This repo deliberately does not treat raw-data mirroring as part of the project shape.

## Current Reality

The repo now has a canonical recovered notebook, a matching script entry point, and a separate legacy archive copy.

- `Xwines.ipynb` is the notebook that follows the finished slides in sample mode and can be switched to a fuller reproduction path.
- `Xwines.py` mirrors that same workflow for terminal-based reruns.
- `docs/legacy/Xwines-original.ipynb` preserves the broken original notebook for recovery context.

The biggest remaining gap is no longer notebook structure. It is result fidelity: if we want to match the June 14, 2024 slides even more closely, the next step is to tune the full-data path and appendix settings against the recovered cleaned inputs.
