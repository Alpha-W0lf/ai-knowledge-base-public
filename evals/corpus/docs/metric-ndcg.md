# Normalised discounted cumulative gain (nDCG)

nDCG measures ranking quality with graded relevance labels and a discount for lower positions. Each result has a relevance grade, for example 2 for "answers the question", 1 for "related" and 0 for "not relevant". The gain of a result is usually 2^grade - 1, so a highly relevant result is worth much more than a related one.

## The three steps

Discounted cumulative gain (DCG) adds the gains of the top k results, dividing each by log2(rank + 1). The result at rank 1 is divided by 1, rank 2 by about 1.58, rank 3 by 2, and so on, so lower positions count less.

The ideal DCG (IDCG) is the DCG of the best possible ordering: all the judged documents sorted by grade, highest first, cut at k.

nDCG@k is DCG divided by IDCG. It ranges from 0 to 1, where 1 means the system produced the ideal ordering within the top k. Normalising makes queries with many relevant documents comparable with queries that have only one.

## Why graded labels help

Binary metrics treat a passage that fully answers the question and one that only mentions the topic as equally good. Graded labels let the metric reward a system that puts the full answer above the partial one. They also handle look-alike documents gracefully: a near-miss document labelled 1 earns some credit, while a fully relevant one labelled 2 earns more.

## Practical notes

Always state the cut-off: nDCG@10 is common for search, and nDCG@3 or @5 for answer generation that only reads a few passages. Unjudged documents are usually treated as grade 0, which penalises systems that surface relevant documents nobody labelled; review a sample of high-ranked unjudged results when a new system scores unexpectedly low.

nDCG values from different datasets are not comparable, because they depend on how many relevant documents each query has and how the grades were assigned. Compare systems on the same queries and labels, and use paired statistics across queries for the difference rather than eyeballing two averages.
