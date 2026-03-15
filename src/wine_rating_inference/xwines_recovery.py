from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from .project_status import project_root


RunMode = Literal["sample", "full"]

RECOMMENDATION_COLUMNS = [
    "UserID",
    "WineID",
    "Vintage",
    "Rating",
    "Date",
    "WineName",
    "Type",
    "WineryID",
    "WineryName",
]

CLASSIFICATION_COLUMNS = [
    "UserID",
    "WineID",
    "Vintage",
    "Rating",
    "Date",
    "WineName",
    "Type",
    "Elaborate",
    "Grapes",
    "ABV",
    "Body",
    "Acidity",
    "WineryID",
    "WineryName",
]

DATA_OVERVIEW_COLUMNS = [
    "WineID",
    "Type",
    "Elaborate",
    "Grapes",
    "ABV",
    "Body",
    "Acidity",
    "Country",
    "WineryName",
]


@dataclass(frozen=True)
class NotebookRunConfig:
    run_mode: RunMode = "sample"
    panel_relative_path: str = "data/cleaned/Xwines.csv"
    wine_catalog_relative_path: str = "data/cleaned/100K_Wines.csv"
    sample_nrows: int = 300_000
    sample_min_label_count: int = 100
    full_min_label_count: int = 500
    familywise_alpha: float = 0.05
    top_n: int = 25
    random_seed: int = 7
    sample_classification_rows: int = 12_000
    full_classification_rows: int = 50_000

    @property
    def minimum_label_count(self) -> int:
        return self.sample_min_label_count if self.run_mode == "sample" else self.full_min_label_count

    @property
    def classification_row_cap(self) -> int:
        return self.sample_classification_rows if self.run_mode == "sample" else self.full_classification_rows

    @property
    def panel_path(self) -> Path:
        return project_root() / self.panel_relative_path

    @property
    def wine_catalog_path(self) -> Path:
        return project_root() / self.wine_catalog_relative_path


@dataclass(frozen=True)
class RecommendationResult:
    baseline_key: str
    baseline_display: str
    baseline_mean: float
    df_resid: int
    residual_mse: float
    coefficient_table: Any
    bonferroni_table: Any
    bonferroni_threshold: float
    label_summary: Any


@dataclass(frozen=True)
class ClassificationResult:
    dataset_size: int
    positive_share: float
    confusion_matrix: Any
    report: dict[str, Any]
    extra: dict[str, Any]


def default_config(run_mode: RunMode = "sample") -> NotebookRunConfig:
    return NotebookRunConfig(run_mode=run_mode)


def load_panel(config: NotebookRunConfig, columns: list[str] | None = None) -> Any:
    import pandas as pd

    usecols = columns or CLASSIFICATION_COLUMNS
    read_kwargs: dict[str, Any] = {
        "usecols": usecols,
        "dtype": {
            "UserID": "string",
            "WineID": "string",
            "Vintage": "string",
            "WineName": "string",
            "Type": "string",
            "Elaborate": "string",
            "Grapes": "string",
            "Body": "string",
            "Acidity": "string",
            "WineryID": "string",
            "WineryName": "string",
        },
        "parse_dates": ["Date"],
    }
    if "ABV" in usecols:
        read_kwargs["dtype"]["ABV"] = "float64"
    if config.run_mode == "sample":
        read_kwargs["nrows"] = config.sample_nrows
    return pd.read_csv(config.panel_path, **read_kwargs)


def load_wine_catalog(config: NotebookRunConfig) -> Any:
    import pandas as pd

    return pd.read_csv(
        config.wine_catalog_path,
        usecols=DATA_OVERVIEW_COLUMNS,
        dtype={
            "WineID": "string",
            "Type": "string",
            "Elaborate": "string",
            "Grapes": "string",
            "Body": "string",
            "Acidity": "string",
            "Country": "string",
            "WineryName": "string",
        },
    )


def build_data_overview(config: NotebookRunConfig) -> dict[str, Any]:
    catalog = load_wine_catalog(config)
    cardinality_columns = ["Type", "Acidity", "Grapes", "Body", "Country", "WineryName"]
    cardinalities = {column: int(catalog[column].nunique(dropna=True)) for column in cardinality_columns}
    return {
        "catalog_rows": int(len(catalog)),
        "candidate_cardinality_sum": int(sum(cardinalities.values())),
        "candidate_cardinalities": cardinalities,
    }


def _normalize_text(series: Any, fallback: str) -> Any:
    normalized = series.fillna(fallback).astype("string").str.strip()
    return normalized.replace({"": fallback, "<NA>": fallback})


def add_label_columns(frame: Any) -> Any:
    enriched = frame.copy()
    vintage = _normalize_text(enriched["Vintage"], "Unknown")
    winery_id = _normalize_text(enriched["WineryID"], "missing-winery")
    winery_name = _normalize_text(enriched["WineryName"], "Unknown Winery")
    enriched["Vintage"] = vintage
    enriched["WineryID"] = winery_id
    enriched["WineryName"] = winery_name
    enriched["label_key"] = winery_id + "_" + vintage
    enriched["label_display"] = winery_name + " " + vintage
    return enriched


def deduplicate_recent_user_wine_ratings(frame: Any) -> Any:
    deduped = frame.sort_values("Date").drop_duplicates(["UserID", "WineID"], keep="last")
    return deduped.reset_index(drop=True)


def prepare_red_wine_frame(config: NotebookRunConfig) -> tuple[Any, Any, dict[str, Any]]:
    panel = load_panel(config, CLASSIFICATION_COLUMNS)
    panel["Rating"] = panel["Rating"].astype(float)
    red = panel[panel["Type"] == "Red"].copy()
    deduped = deduplicate_recent_user_wine_ratings(red)
    deduped = add_label_columns(deduped)
    label_counts = deduped["label_key"].value_counts().rename_axis("label_key").reset_index(name="rating_count")
    eligible_keys = label_counts[label_counts["rating_count"] >= config.minimum_label_count]["label_key"]
    eligible = deduped[deduped["label_key"].isin(set(eligible_keys))].copy()
    summary = {
        "loaded_rows": int(len(panel)),
        "red_rows": int(len(red)),
        "deduped_rows": int(len(deduped)),
        "eligible_rows": int(len(eligible)),
        "eligible_labels": int(eligible["label_key"].nunique()),
        "minimum_label_count": config.minimum_label_count,
    }
    return deduped, eligible, summary


def aggregate_recommendation_frame(eligible_frame: Any) -> Any:
    aggregated = (
        eligible_frame.groupby(
            ["WineID", "WineName", "label_key", "label_display", "WineryName", "Vintage"],
            as_index=False,
        )["Rating"]
        .mean()
        .sort_values(["label_display", "WineName"])
        .reset_index(drop=True)
    )
    return aggregated


def slide_groupby_snippet() -> str:
    return "df = df.groupby(['WineID', 'Label'])['Rating'].mean().reset_index()"


def fit_recommendation_model(
    aggregated_frame: Any,
    familywise_alpha: float = 0.05,
    top_n: int = 25,
) -> RecommendationResult:
    import numpy as np
    import pandas as pd
    from scipy import stats

    label_summary = (
        aggregated_frame.groupby(["label_key", "label_display"], as_index=False)
        .agg(group_size=("Rating", "size"), group_mean=("Rating", "mean"))
        .sort_values(["group_mean", "label_key"], ascending=[True, True])
        .reset_index(drop=True)
    )

    baseline_row = label_summary.iloc[0]
    baseline_key = str(baseline_row["label_key"])
    baseline_display = str(baseline_row["label_display"])
    baseline_mean = float(baseline_row["group_mean"])
    baseline_size = int(baseline_row["group_size"])

    mean_lookup = label_summary[["label_key", "group_mean"]].rename(columns={"group_mean": "group_mean_lookup"})
    residual_frame = aggregated_frame.merge(mean_lookup, on="label_key", how="left")
    residuals = residual_frame["Rating"] - residual_frame["group_mean_lookup"]
    sse = float((residuals**2).sum())
    observation_count = int(len(aggregated_frame))
    group_count = int(label_summary["label_key"].nunique())
    df_resid = observation_count - group_count
    residual_mse = sse / df_resid if df_resid > 0 else float("nan")

    rows = []
    for row in label_summary.itertuples(index=False):
        label_key = str(row.label_key)
        coefficient = float(row.group_mean - baseline_mean)
        if label_key == baseline_key or residual_mse != residual_mse:
            standard_error = np.nan
            t_value = np.nan
            p_value = np.nan
            is_reference = True
        else:
            standard_error = float(np.sqrt(residual_mse * ((1 / row.group_size) + (1 / baseline_size))))
            t_value = float(coefficient / standard_error) if standard_error else np.nan
            p_value = float(2 * stats.t.sf(abs(t_value), df_resid))
            is_reference = False
        rows.append(
            {
                "label_key": label_key,
                "label_display": str(row.label_display),
                "group_size": int(row.group_size),
                "group_mean": float(row.group_mean),
                "coefficient": coefficient,
                "standard_error": standard_error,
                "t_value": t_value,
                "p_value": p_value,
                "is_reference": is_reference,
            }
        )

    coefficient_table = pd.DataFrame(rows).sort_values(
        ["coefficient", "t_value", "label_display"],
        ascending=[False, False, True],
    )
    bonferroni_threshold = familywise_alpha / max(top_n, 1)
    bonferroni_table = (
        coefficient_table[
            (~coefficient_table["is_reference"])
            & (coefficient_table["coefficient"] > 0)
            & (coefficient_table["p_value"] <= bonferroni_threshold)
        ]
        .head(top_n)
        .reset_index(drop=True)
    )

    return RecommendationResult(
        baseline_key=baseline_key,
        baseline_display=baseline_display,
        baseline_mean=baseline_mean,
        df_resid=df_resid,
        residual_mse=residual_mse,
        coefficient_table=coefficient_table.reset_index(drop=True),
        bonferroni_table=bonferroni_table,
        bonferroni_threshold=bonferroni_threshold,
        label_summary=label_summary,
    )


def build_classification_frame(deduped_red_frame: Any, max_rows: int, random_seed: int) -> Any:
    import pandas as pd

    extremes = deduped_red_frame[
        (deduped_red_frame["Rating"] <= 1.0) | (deduped_red_frame["Rating"] >= 4.0)
    ].copy()
    low = extremes[extremes["Rating"] <= 1.0].copy()
    high = extremes[extremes["Rating"] >= 4.0].copy()
    if low.empty or high.empty:
        balanced = extremes
    else:
        per_class_cap = min(len(low), len(high), max_rows // 2)
        low = low.sample(n=per_class_cap, random_state=random_seed)
        high = high.sample(n=per_class_cap, random_state=random_seed)
        balanced = pd.concat([low, high], ignore_index=True)
    balanced = balanced.sort_values("Date").reset_index(drop=True)
    balanced["target"] = (balanced["Rating"] >= 4.0).astype(int)
    return balanced[
        ["Elaborate", "Grapes", "ABV", "Body", "Acidity", "target"]
    ].dropna(subset=["Elaborate", "Grapes", "ABV", "Body", "Acidity"])


def run_naive_bayes_appendix(
    deduped_red_frame: Any,
    max_rows: int,
    random_seed: int,
) -> ClassificationResult:
    from sklearn.compose import ColumnTransformer
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.model_selection import train_test_split
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

    classification_frame = build_classification_frame(deduped_red_frame, max_rows=max_rows, random_seed=random_seed)
    X = classification_frame[["Elaborate", "Grapes", "ABV", "Body", "Acidity"]]
    y = classification_frame["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=random_seed,
        stratify=y,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), ["Elaborate", "Grapes", "Body", "Acidity"]),
            ("numeric", MinMaxScaler(), ["ABV"]),
        ]
    )
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", MultinomialNB()),
        ]
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    matrix = confusion_matrix(y_test, predictions)
    report = classification_report(y_test, predictions, output_dict=True, zero_division=0)
    return ClassificationResult(
        dataset_size=int(len(classification_frame)),
        positive_share=float(y.mean()),
        confusion_matrix=matrix,
        report=report,
        extra={
            "trace_share": float(matrix.trace() / matrix.sum()),
        },
    )


def run_decision_tree_appendix(
    deduped_red_frame: Any,
    max_rows: int,
    random_seed: int,
) -> ClassificationResult:
    from scipy.stats import randint
    from sklearn.compose import ColumnTransformer
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.model_selection import RandomizedSearchCV, train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.tree import DecisionTreeClassifier

    classification_frame = build_classification_frame(deduped_red_frame, max_rows=max_rows, random_seed=random_seed)
    X = classification_frame[["Elaborate", "Grapes", "ABV", "Body", "Acidity"]]
    y = classification_frame["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=random_seed,
        stratify=y,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), ["Elaborate", "Grapes", "Body", "Acidity"]),
            ("numeric", "passthrough", ["ABV"]),
        ]
    )
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", DecisionTreeClassifier(random_state=random_seed)),
        ]
    )
    param_distributions = {
        "classifier__criterion": ["gini", "entropy"],
        "classifier__max_depth": randint(10, 30),
        "classifier__min_samples_split": randint(5, 20),
        "classifier__min_samples_leaf": randint(2, 10),
    }
    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=param_distributions,
        n_iter=10,
        cv=5,
        scoring="precision",
        random_state=random_seed,
        n_jobs=1,
    )
    search.fit(X_train, y_train)
    predictions = search.best_estimator_.predict(X_test)
    matrix = confusion_matrix(y_test, predictions)
    report = classification_report(y_test, predictions, output_dict=True, zero_division=0)
    return ClassificationResult(
        dataset_size=int(len(classification_frame)),
        positive_share=float(y.mean()),
        confusion_matrix=matrix,
        report=report,
        extra={
            "best_params": search.best_params_,
        },
    )
