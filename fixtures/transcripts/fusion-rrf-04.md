# Rank fusion with reciprocal rank fusion

Reciprocal rank fusion, often abbreviated RRF, combines ranked lists from vector ANN
and full-text search without needing calibrated scores.

For each chunk id, add 1/(k + rank) from each retriever leg, then sort. The fused
shortlist of size N feeds the cross-encoder. Placeholder for fixture:fusion-rrf-04.
