from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectAsset:
    label: str
    relative_path: str
    required: bool = True
    description: str = ""


CORE_ASSETS = (
    ProjectAsset(
        label="official_slides",
        relative_path="docs/slides/xwines-final-slides.pdf",
        description="Canonical finished presentation artifact.",
    ),
    ProjectAsset(
        label="slides_summary",
        relative_path="docs/slides/README.md",
        description="Narrative summary of the completed slides.",
    ),
    ProjectAsset(
        label="project_status_doc",
        relative_path="docs/project-status.md",
        description="Repo-level status and next-step document.",
    ),
    ProjectAsset(
        label="legacy_notebook",
        relative_path="Xwines.ipynb",
        description="Recovered exploratory notebook from the original project.",
    ),
    ProjectAsset(
        label="cleaned_panel",
        relative_path="data/cleaned/Xwines.csv",
        required=False,
        description="Recovered cleaned panel used in earlier work.",
    ),
    ProjectAsset(
        label="cleaned_ratings",
        relative_path="data/cleaned/21M_Ratings.csv",
        required=False,
        description="Recovered cleaned ratings source.",
    ),
)


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def human_size(size_in_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size_in_bytes)
    unit = units[0]
    for unit in units:
        if value < 1024 or unit == units[-1]:
            break
        value /= 1024
    if unit == "B":
        return f"{int(value)} {unit}"
    return f"{value:.1f} {unit}"


def collect_assets() -> list[tuple[ProjectAsset, Path, bool]]:
    root = project_root()
    results: list[tuple[ProjectAsset, Path, bool]] = []
    for asset in CORE_ASSETS:
        path = root / asset.relative_path
        results.append((asset, path, path.exists()))
    return results


def render_report() -> str:
    root = project_root()
    lines = [
        "Wine Rating Inference Project Status",
        f"Project root: {root}",
        "",
    ]
    for asset, path, exists in collect_assets():
        status = "OK" if exists else "MISSING"
        size = human_size(path.stat().st_size) if exists and path.is_file() else "-"
        requirement = "required" if asset.required else "optional"
        lines.append(f"- {asset.label}: {status} ({requirement}, {size})")
        lines.append(f"  path: {path}")
        if asset.description:
            lines.append(f"  note: {asset.description}")
    return "\n".join(lines)


def main() -> int:
    print(render_report())
    missing_required = any(
        asset.required and not exists for asset, _, exists in collect_assets()
    )
    return 1 if missing_required else 0


if __name__ == "__main__":
    raise SystemExit(main())

