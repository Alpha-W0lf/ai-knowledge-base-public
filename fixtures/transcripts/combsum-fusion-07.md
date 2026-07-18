# Rank fusion with CombSUM score summing

CombSUM combines ranked lists from vector ANN and full-text search by summing
normalized retriever scores for each chunk id, then sorting the fused shortlist.

Unlike reciprocal rank fusion, CombSUM needs comparable score scales and does
not use the 1/(k + rank) term. The fused shortlist of size N can still feed a
later reranker. Placeholder for fixture:combsum-fusion-07.
