# Recall at k and hit rate for first-stage retrieval

Recall@k is the share of all relevant documents for a query that appear in the top k results, averaged over queries. Hit rate@k, sometimes called success@k, is the share of queries with at least one relevant document in the top k. When each query has exactly one relevant document, the two are the same.

These are the right metrics for a first-stage retriever whose job is to build a shortlist for something downstream, such as a reranker or a language model. The downstream stage can only use what the first stage hands over, so the question is whether the right material made it into the shortlist, not where it sits inside it.

## Choosing k

Set k to the size of the shortlist actually passed downstream. If a cross-encoder reranks the top 30, measure recall@30; if a language model reads the top 5 passages, measure recall@5. Reporting recall@100 for a system that only uses the top 5 overstates what users experience.

## The ceiling effect

Recall@k says nothing about order inside the top k. On a small corpus it can also be close to meaningless. If a collection has eight documents and the system returns five of them for every query, a random ordering already includes the right document most of the time, and recall@5 near 1.0 shows only that the pipeline runs. Always compare against a random baseline, and make sure k is small relative to the corpus size.

## Pairing with rank-aware metrics

Use recall@k for the retrieval stage and a rank-aware metric such as MRR or nDCG for the final ordering. A reranker that improves nDCG without changing recall is reordering well; a change that lowers recall at the shortlist size will cap every downstream metric no matter how good the reranker is.

## Labels limit the metric

Recall needs to know every relevant document for a query. In large collections nobody can label everything, so recall is computed against the known relevant set, and new relevant documents that the system finds count as misses. Pooling, labelling the union of top results from several systems, reduces this bias.
