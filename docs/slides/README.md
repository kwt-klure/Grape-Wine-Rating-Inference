# Official Slides

This folder contains the canonical finished presentation for the project:

- [xwines-final-slides.pdf](xwines-final-slides.pdf)

## Deck Summary

The slide deck frames the project around a practical question: how can consumers and wine importers identify highly rated wines using features that are observable in the market, rather than lab-style chemical measurements?

The presentation starts from the X-Wines dataset and an OLS-style feature specification using `Type`, `Acidity`, `Grapes`, `Body`, `Country`, `Vintage`, and related wine descriptors. It then explains why this approach breaks down in practice because of the extremely high-cardinality categorical space and the resulting curse of dimensionality.

The main modeling pivot is to treat `winery × vintage` as a proxy for many hard-to-model wine characteristics. The deck argues that winery technique and year-specific climate capture a meaningful share of variation in taste-related outcomes.

The data-cleaning section documents four concrete rules used before estimation:

- keep only the most recent rating when the same user rated the same wine multiple times
- focus on red wines first
- drop `winery × vintage` combinations with fewer than 500 ratings
- average ratings across users for the same wine label

From there, the presentation moves into large-scale inference. It notes the instability of interpreting thousands of OLS coefficients directly, then uses Bonferroni-style reasoning to build a recommendation list whose family-wise Type I error is controlled. This is the logic behind the ranked list of highly recommended wines in the results section.

The later slides extend the project beyond the recommendation framing. They introduce a Naive Bayes classifier using `Elaborate`, `Grapes`, `ABV`, `Body`, and `Acidity`, then a classification-tree approach with randomized cross-validation for hyperparameter search. The deck reports that the Naive Bayes results were not very satisfactory, while the tree model reached precision values of 0.75 and 0.78 in the confusion-matrix summary.

## Notes

- Slide count: 23 pages
- Presentation date shown in the deck: June 14, 2024
- This PDF is the authoritative presentation artifact for the project
- Earlier Notion materials are preserved separately under [../ppt-notion/README.md](../ppt-notion/README.md)
