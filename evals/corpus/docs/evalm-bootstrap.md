# Bootstrap confidence intervals for retrieval metrics

A retrieval metric computed on 50 queries is an estimate, and so is the difference between two systems measured on those queries. The bootstrap is a simple way to put an interval around that estimate without assuming any particular distribution.

## The paired bootstrap

To compare system A with system B, compute the per-query metric for both, for example nDCG@10 for each query. Then repeat a few thousand times: draw a sample of queries with replacement, the same size as the original set, and compute the mean difference between A and B on that sample. The 2.5th and 97.5th percentiles of those resampled differences form a 95 percent confidence interval for the true difference.

Pairing matters. Queries vary enormously in difficulty, and that variation affects both systems the same way. Resampling queries and computing the difference within each resample removes the shared difficulty, which gives a much tighter interval than comparing two separately bootstrapped means.

## Reading the interval

If the interval for B minus A lies entirely above zero, the data support B being better on queries like these. If it straddles zero, the measured difference could be noise, however large the point estimate looks. With small query sets, intervals are wide, and "no detectable difference" is a common and legitimate result.

## Pitfalls

The bootstrap assumes the queries are a representative sample of the queries you care about. Fifty paraphrases of five questions are not fifty independent queries; resample at the level of the underlying topic in that case. Fix the random seed so the interval is reproducible, and report the number of resamples.

Running many comparisons inflates false positives: test twenty configurations and one will look significant by chance. Decide the comparisons in advance, ideally in a pre-registration document, and treat anything else as exploratory.

## Alternatives

A paired t-test or a Wilcoxon signed-rank test on per-query differences gives similar conclusions on most retrieval data. A permutation test, which randomly swaps the system labels within each query, is another distribution-free option. The bootstrap is popular because the same code produces intervals for any metric, including awkward ones like nDCG.
