# Cross-encoder rerank shortlist

A cross-encoder scores the query and a passage together. It is too slow for the whole
corpus, so retrieve broadly, fuse to N candidates, then rerank to K results.

If the local cross-encoder fails, degrade honestly to fused ranks and label the stage
fusion_degraded. Placeholder for fixture:cross-encoder-05.
