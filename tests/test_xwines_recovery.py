from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pandas as pd

from wine_rating_inference.xwines_recovery import (
    add_label_columns,
    aggregate_recommendation_frame,
    deduplicate_recent_user_wine_ratings,
    fit_recommendation_model,
)


class XwinesRecoveryTests(unittest.TestCase):
    def test_deduplicate_recent_user_wine_ratings_keeps_latest_row(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "UserID": "u1",
                    "WineID": "w1",
                    "Date": pd.Timestamp("2024-01-01"),
                    "Type": "Red",
                    "Vintage": "2015",
                    "WineryID": "100",
                    "WineryName": "Alpha",
                    "Rating": 2.0,
                },
                {
                    "UserID": "u1",
                    "WineID": "w1",
                    "Date": pd.Timestamp("2024-02-01"),
                    "Type": "Red",
                    "Vintage": "2015",
                    "WineryID": "100",
                    "WineryName": "Alpha",
                    "Rating": 4.0,
                },
                {
                    "UserID": "u2",
                    "WineID": "w2",
                    "Date": pd.Timestamp("2024-01-15"),
                    "Type": "Red",
                    "Vintage": "2016",
                    "WineryID": "101",
                    "WineryName": "Beta",
                    "Rating": 5.0,
                },
            ]
        )
        deduped = deduplicate_recent_user_wine_ratings(frame)
        self.assertEqual(len(deduped), 2)
        kept = deduped.loc[deduped["WineID"] == "w1", "Rating"].iloc[0]
        self.assertEqual(kept, 4.0)

    def test_add_label_columns_builds_stable_key_and_display(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "WineID": "w1",
                    "Vintage": "2015",
                    "WineryID": "100",
                    "WineryName": "Alpha",
                }
            ]
        )
        labeled = add_label_columns(frame)
        self.assertEqual(labeled.loc[0, "label_key"], "100_2015")
        self.assertEqual(labeled.loc[0, "label_display"], "Alpha 2015")

    def test_aggregate_recommendation_frame_returns_one_row_per_wine_label(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "WineID": "w1",
                    "WineName": "Wine One",
                    "label_key": "100_2015",
                    "label_display": "Alpha 2015",
                    "WineryName": "Alpha",
                    "Vintage": "2015",
                    "Rating": 4.0,
                },
                {
                    "WineID": "w1",
                    "WineName": "Wine One",
                    "label_key": "100_2015",
                    "label_display": "Alpha 2015",
                    "WineryName": "Alpha",
                    "Vintage": "2015",
                    "Rating": 5.0,
                },
                {
                    "WineID": "w2",
                    "WineName": "Wine Two",
                    "label_key": "101_2016",
                    "label_display": "Beta 2016",
                    "WineryName": "Beta",
                    "Vintage": "2016",
                    "Rating": 3.0,
                },
            ]
        )
        aggregated = aggregate_recommendation_frame(frame)
        self.assertEqual(len(aggregated), 2)
        self.assertAlmostEqual(
            aggregated.loc[aggregated["WineID"] == "w1", "Rating"].iloc[0],
            4.5,
        )

    def test_bonferroni_filter_returns_stable_ranked_subset(self) -> None:
        rows = []
        for idx in range(12):
            rows.append(
                {
                    "WineID": f"a{idx}",
                    "WineName": f"Alpha {idx}",
                    "label_key": "100_2010",
                    "label_display": "Alpha 2010",
                    "WineryName": "Alpha",
                    "Vintage": "2010",
                    "Rating": 1.0 + (idx % 2) * 0.1,
                }
            )
            rows.append(
                {
                    "WineID": f"b{idx}",
                    "WineName": f"Beta {idx}",
                    "label_key": "200_2014",
                    "label_display": "Beta 2014",
                    "WineryName": "Beta",
                    "Vintage": "2014",
                    "Rating": 4.8 + (idx % 2) * 0.05,
                }
            )
            rows.append(
                {
                    "WineID": f"c{idx}",
                    "WineName": f"Gamma {idx}",
                    "label_key": "300_2016",
                    "label_display": "Gamma 2016",
                    "WineryName": "Gamma",
                    "Vintage": "2016",
                    "Rating": 4.2 + (idx % 2) * 0.05,
                }
            )
        aggregated = pd.DataFrame(rows)
        result = fit_recommendation_model(aggregated, familywise_alpha=0.05, top_n=2)
        self.assertEqual(result.baseline_display, "Alpha 2010")
        self.assertEqual(list(result.bonferroni_table["label_display"]), ["Beta 2014", "Gamma 2016"])


if __name__ == "__main__":
    unittest.main()
