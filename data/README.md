# Data Assets

`data/cleaned/` is the canonical local input area for the recovered project.

The current workspace contains four recovered cleaned assets:

- `100K_Wines.csv`
- `21M_Ratings.csv`
- `Xwines.csv`
- `df.csv`

These files were recovered from the cleaned-data source referenced by the original repo. They are intentionally kept separate from the raw X-Wines source, which remains reference-only and is not mirrored locally in this project.

Because the recovered cleaned CSV files are extremely large, they are kept in the project workspace as local inputs but are not committed to GitHub as normal tracked source files.

## Guidance

- Treat these files as local research assets rather than generated build output.
- Use `Xwines.csv` and `df.csv` cautiously: they are legacy cleaned artifacts from the earlier project state and should be validated as the codebase becomes reproducible.
- Keep future derived outputs outside `data/cleaned/` unless they are promoted to canonical project inputs.
