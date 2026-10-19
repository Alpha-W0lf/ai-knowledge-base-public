# Weighted linear interpolation between dense and sparse scores

Many vector databases expose hybrid search through a single parameter, often called alpha. The fused score is alpha times the normalised dense score plus (1 - alpha) times the normalised sparse score. Alpha = 1 is pure vector search, alpha = 0 is pure keyword search, and values in between blend the two.

The model is easy to explain to stakeholders, and alpha can be tuned per collection or even per query type. Product search, where users type exact model numbers, often prefers a low alpha that leans on keywords. Question answering over prose often prefers a higher alpha.

## Tuning alpha without fooling yourself

Alpha is a hyperparameter, so it must be tuned on a dev set and confirmed on a separate held-out set. Sweep a small grid, such as 0.0 to 1.0 in steps of 0.1, and plot nDCG@10 against alpha. A flat curve means the choice barely matters and a default like 0.5 is fine. A sharp peak on dev that does not reappear on held-out queries is a sign of overfitting to a small query set.

The best alpha also moves when anything upstream changes. A new embedding model changes the dense score distribution. A new tokenizer or stemming rule changes BM25 scores. Each change needs a re-sweep, which is a real maintenance cost compared with rank-based fusion that has no weight to tune.

## Normalisation still matters

Linear interpolation inherits every normalisation problem of score fusion. Min-max scaling per query is the usual choice. Some engines apply a fixed transform instead, for example mapping BM25 through a saturating function so that very long or very keyword-dense documents do not dominate. Whatever the transform, record it with the alpha value, because the two only make sense together.

## Dynamic weighting

A step beyond a fixed alpha is to predict the weight per query. A small classifier can look at query length, the presence of quoted phrases, identifiers or rare tokens, and choose a lower alpha for lookup-style queries. This adds a model to train and monitor. Before building it, check how much of the gap a fixed alpha or rank fusion already closes on your own labelled queries.
