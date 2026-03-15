from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wine_rating_inference.xwines_recovery import (
    NotebookRunConfig,
    aggregate_recommendation_frame,
    build_data_overview,
    fit_recommendation_model,
    load_wine_catalog,
    prepare_red_wine_frame,
    run_decision_tree_appendix,
    run_naive_bayes_appendix,
    slide_groupby_snippet,
)


pd.options.display.max_columns = 20
pd.options.display.float_format = "{:,.6f}".format


def section(title: str) -> None:
    print()
    print(title)
    print("=" * len(title))


def print_series(values: pd.Series | dict[str, object]) -> None:
    series = values if isinstance(values, pd.Series) else pd.Series(values)
    print(series.to_string())


def print_frame(frame: pd.DataFrame, rows: int = 10) -> None:
    preview = frame.head(rows)
    print(preview.to_string())


def confusion_matrix_frame(matrix: object) -> pd.DataFrame:
    return pd.DataFrame(
        matrix,
        index=["actual_0", "actual_1"],
        columns=["pred_0", "pred_1"],
    )


def build_config(run_mode: str) -> NotebookRunConfig:
    return NotebookRunConfig(
        run_mode=run_mode,
        top_n=15 if run_mode == "sample" else 50,
        sample_nrows=300_000,
        sample_min_label_count=100,
        full_min_label_count=500,
        sample_classification_rows=10_000,
        full_classification_rows=50_000,
    )


def run_analysis(config: NotebookRunConfig) -> None:
    section("Experiment: Recovering X-Wines Final Slide Analysis")
    print(
        "Objective: recover the final-slide workflow in a script form that mirrors "
        "the canonical notebook."
    )
    print_series(
        {
            "project_root": ".",
            "script_path": "Xwines.py",
            "run_mode": config.run_mode,
            "panel_path": str(config.panel_path.relative_to(ROOT)),
            "minimum_label_count": config.minimum_label_count,
            "classification_row_cap": config.classification_row_cap,
        }
    )

    section("Data Overview Tied To The Slides")
    overview = build_data_overview(config)
    catalog = load_wine_catalog(config)
    print_series(overview)
    print()
    print_frame(catalog, rows=5)

    section("Initial OLS Framing And The Dimensionality Problem")
    cardinality_frame = (
        pd.Series(overview["candidate_cardinalities"], name="unique_values")
        .sort_values(ascending=False)
        .to_frame()
    )
    print_frame(cardinality_frame, rows=len(cardinality_frame))
    print()
    print_series(
        {
            "candidate_cardinality_sum": overview["candidate_cardinality_sum"],
            "slide_message": (
                "The finished deck treats this as a curse-of-dimensionality problem "
                "before moving to winery × vintage."
            ),
        }
    )

    section("Sommelier's Knowledge And The winery × vintage Pivot")
    deduped_red, eligible_red, cleaning_summary = prepare_red_wine_frame(config)
    label_count_preview = (
        eligible_red["label_display"]
        .value_counts()
        .rename_axis("label_display")
        .reset_index(name="rating_count")
        .head(10)
    )
    print_series(cleaning_summary)
    print()
    print_frame(label_count_preview, rows=len(label_count_preview))

    section("Data Processing & Cleansing")
    aggregated = aggregate_recommendation_frame(eligible_red)
    print_frame(aggregated, rows=10)
    print()
    print_series(
        {
            "aggregated_rows": len(aggregated),
            "eligible_labels": int(aggregated["label_key"].nunique()),
            "slide_groupby_snippet": slide_groupby_snippet(),
        }
    )

    section("Recommendation Model, Significance Screening, And Top List")
    recommendation = fit_recommendation_model(
        aggregated,
        familywise_alpha=config.familywise_alpha,
        top_n=config.top_n,
    )
    print_series(
        {
            "baseline_display": recommendation.baseline_display,
            "baseline_mean": recommendation.baseline_mean,
            "df_resid": recommendation.df_resid,
            "residual_mse": recommendation.residual_mse,
            "bonferroni_threshold": recommendation.bonferroni_threshold,
        }
    )
    print()
    print_frame(recommendation.coefficient_table, rows=15)
    print()
    top_recommendations = recommendation.bonferroni_table[
        ["label_display", "coefficient", "t_value", "p_value", "group_mean", "group_size"]
    ].rename(
        columns={
            "label_display": "Wine",
            "coefficient": "Coefficient",
            "t_value": "t-value",
            "p_value": "P-value",
            "group_mean": "Mean Rating",
            "group_size": "Wine Count",
        }
    )
    print_frame(top_recommendations, rows=len(top_recommendations))

    section("Winery Aspect / Interpretation")
    raw_significant_count = int(
        recommendation.coefficient_table["p_value"].le(0.05).fillna(False).sum()
    )
    print_series(
        {
            "labels_in_model": int(recommendation.label_summary["label_key"].nunique()),
            "coefficients_below_0.05": raw_significant_count,
            "bonferroni_selected": int(len(recommendation.bonferroni_table)),
        }
    )
    print()
    top_label_summary = recommendation.label_summary.sort_values(
        ["group_mean", "group_size"],
        ascending=[False, False],
    )
    print_frame(top_label_summary, rows=10)

    section("Appendix: Naive Bayes For Red Wine")
    nb_result = run_naive_bayes_appendix(
        deduped_red_frame=deduped_red,
        max_rows=config.classification_row_cap,
        random_seed=config.random_seed,
    )
    nb_report = pd.DataFrame(nb_result.report).T.loc[
        ["0", "1", "accuracy", "macro avg", "weighted avg"]
    ]
    print_series(
        {
            "dataset_size": nb_result.dataset_size,
            "positive_share": nb_result.positive_share,
            "trace_share": nb_result.extra["trace_share"],
            "precision_class_0": nb_result.report["0"]["precision"],
            "precision_class_1": nb_result.report["1"]["precision"],
        }
    )
    print()
    print_frame(confusion_matrix_frame(nb_result.confusion_matrix), rows=2)
    print()
    print_frame(nb_report, rows=len(nb_report))

    section("Appendix: Decision Tree")
    tree_result = run_decision_tree_appendix(
        deduped_red_frame=deduped_red,
        max_rows=config.classification_row_cap,
        random_seed=config.random_seed,
    )
    tree_report = pd.DataFrame(tree_result.report).T.loc[
        ["0", "1", "accuracy", "macro avg", "weighted avg"]
    ]
    print_series(
        {
            "dataset_size": tree_result.dataset_size,
            "positive_share": tree_result.positive_share,
            "best_params": str(tree_result.extra["best_params"]),
            "precision_class_0": tree_result.report["0"]["precision"],
            "precision_class_1": tree_result.report["1"]["precision"],
        }
    )
    print()
    print_frame(confusion_matrix_frame(tree_result.confusion_matrix), rows=2)
    print()
    print_frame(tree_report, rows=len(tree_report))

    section("Conclusion And Recovery Notes")
    print(
        "This script mirrors the canonical notebook and keeps the same slide-aligned "
        "sample/full execution model."
    )
    print_series(
        {
            "canonical_notebook": "Xwines.ipynb",
            "canonical_script": "Xwines.py",
            "legacy_notebook": "docs/legacy/Xwines-original.ipynb",
            "run_mode": config.run_mode,
            "full_mode_note": "Switch --run-mode to full for the slide-aligned >= 500 label filter.",
        }
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the recovered X-Wines analysis outside Jupyter."
    )
    parser.add_argument(
        "--run-mode",
        choices=["sample", "full"],
        default="sample",
        help="Use sample mode for lightweight committed outputs or full for closer slide reproduction.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = build_config(run_mode=args.run_mode)
    run_analysis(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
