# Mean average precision (MAP)

Mean average precision summarises precision across all the positions where relevant documents appear. For one query, walk down the ranked list. Each time you reach a relevant document, compute precision at that rank: the number of relevant documents seen so far divided by the rank. Average precision (AP) is the mean of those precision values over all relevant documents for the query, counting relevant documents that were never retrieved as zero. MAP is the mean of AP over all queries.

## What it rewards

MAP rewards systems that place all relevant documents early, not just the first one. A query with relevant documents at ranks 1, 2 and 3 gets AP = 1.0. The same documents at ranks 1, 5 and 10 get AP = (1 + 0.4 + 0.3) / 3, about 0.57. This makes MAP a good fit for recall-oriented tasks such as literature search, legal discovery or building a complete context for a report, where users need every relevant document.

## Limitations

MAP uses binary relevance only, so it cannot tell a perfect answer from a passing mention. It is also harder to explain than hit rate or MRR: "average of precision values at each relevant rank" does not translate into an intuitive user experience. And because it depends on the total number of relevant documents, incomplete labels distort it in the same way they distort recall.

## MAP versus nDCG

Both reward putting relevant documents high. nDCG supports graded relevance and uses a smooth logarithmic position discount. MAP uses binary relevance and an implicit discount through precision. In practice the two usually rank systems in the same order; where they disagree, it is often because graded labels separate highly relevant from partly relevant documents.

## Reporting

As with any metric, report the cut-off if one is used, the number of queries, and a confidence interval for differences between systems. For a single-answer question-answering task, MAP reduces to MRR, so reporting both adds nothing; pick the one that matches the task.
