"""Utilities for the recovered wine-rating inference project."""

from .project_status import CORE_ASSETS, ProjectAsset, collect_assets, project_root
from .xwines_recovery import (
    CLASSIFICATION_COLUMNS,
    DATA_OVERVIEW_COLUMNS,
    RECOMMENDATION_COLUMNS,
    NotebookRunConfig,
    RecommendationResult,
    add_label_columns,
    aggregate_recommendation_frame,
    build_data_overview,
    build_classification_frame,
    deduplicate_recent_user_wine_ratings,
    default_config,
    fit_recommendation_model,
    prepare_red_wine_frame,
    run_decision_tree_appendix,
    run_naive_bayes_appendix,
    slide_groupby_snippet,
)

__all__ = [
    "CLASSIFICATION_COLUMNS",
    "CORE_ASSETS",
    "DATA_OVERVIEW_COLUMNS",
    "NotebookRunConfig",
    "ProjectAsset",
    "RECOMMENDATION_COLUMNS",
    "RecommendationResult",
    "add_label_columns",
    "aggregate_recommendation_frame",
    "build_classification_frame",
    "build_data_overview",
    "collect_assets",
    "deduplicate_recent_user_wine_ratings",
    "default_config",
    "fit_recommendation_model",
    "prepare_red_wine_frame",
    "project_root",
    "run_decision_tree_appendix",
    "run_naive_bayes_appendix",
    "slide_groupby_snippet",
]
