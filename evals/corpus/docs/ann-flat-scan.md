# Exact brute-force search: when you do not need an index

The simplest vector search is a flat scan: compute the distance from the query to every stored vector and keep the closest ones. It is exact, with perfect recall by definition, needs no training or tuning, and handles inserts and deletes trivially because there is no structure to maintain.

People often reach for an approximate nearest neighbour index by habit, but for many real workloads a flat scan is fast enough. Modern CPUs compute dot products with SIMD instructions, and scanning is a sequential memory access pattern that hardware handles well.

## Back-of-envelope numbers

A 768-dimensional float32 vector is about 3 KB. Ten thousand of them are 30 MB, which fits in cache-friendly memory and scans in a few milliseconds on a laptop. One hundred thousand vectors take a few tens of milliseconds per query on one core. Somewhere between several hundred thousand and a few million vectors, depending on latency budget and hardware, an index starts to pay for itself.

## Exact search as the ground truth

Even systems that serve queries from an approximate index need exact search for evaluation. Recall of an approximate index is defined against the exact answer, so keep a flat-scan path available and run it on a sample of queries whenever index parameters change. Without that reference, a drop in recall from a badly tuned index is invisible; the system still returns results that look reasonable.

## Small corpora and evaluation sets

For small knowledge bases, test fixtures and evaluation corpora, a flat scan also makes results deterministic. Approximate indexes can return slightly different neighbours depending on build order, random seeds and parameters, which turns into noise in evaluation metrics. A deterministic scan means a metric change reflects a ranking change and nothing else.

## Filtering

A flat scan combines easily with metadata filters: apply the filter first and scan only the matching rows. Approximate indexes need special handling for restrictive filters, because filtering after an approximate search can leave too few results. Many vector databases fall back to a flat scan automatically when no index exists or when a filter is very selective.
