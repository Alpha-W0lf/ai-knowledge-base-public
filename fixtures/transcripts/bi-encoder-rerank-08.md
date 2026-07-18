# Bi-encoder late scoring on a shortlist

A bi-encoder embeds the query and each passage separately, then scores with a
cheap similarity such as dot product. On a fused shortlist of size N it can
rerank to K without joint cross-attention.

Bi-encoder late scoring is not a cross-encoder: it does not score the query and
passage together in one forward pass, and it has no fusion_degraded fail-open
label of its own. Placeholder for fixture:bi-encoder-rerank-08.
