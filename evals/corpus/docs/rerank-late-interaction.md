# Late interaction retrieval with ColBERT-style token vectors

Late interaction keeps one vector per token instead of one vector per passage. ColBERT, introduced by Khattab and Zaharia in 2020, encodes the query and each passage separately, like a bi-encoder, but stores the full matrix of contextualised token embeddings for every passage. Scoring happens late, at query time, with an operation called MaxSim.

For each query token, MaxSim finds the most similar passage token and takes that similarity. The passage score is the sum of those maxima over all query tokens. A query about "rotating API keys" can match "rotation" and "credentials" in different parts of the passage, each contributing its own evidence.

## Where it sits between the two classic designs

Late interaction is a middle ground. Like a bi-encoder, passage representations are precomputed, so queries are fast enough for first-stage retrieval or for reranking large candidate sets. Like a cross-encoder, it compares the query and the passage at the token level, which keeps much of the fine-grained matching that single-vector models lose. In published benchmarks it often lands close to cross-encoder quality at a fraction of the query cost.

## The storage bill

Storing a vector for every token is expensive. A passage of 200 tokens with 128-dimensional vectors needs 25,600 numbers instead of one 768-dimensional vector. ColBERTv2 reduced this with residual compression, storing each token vector as a centroid id plus a small quantised residual, and PLAID added a centroid-based candidate generation step that avoids scoring every passage. Even with these tricks, a late interaction index is several times larger than a single-vector index over the same corpus.

## When to consider it

Late interaction is worth evaluating when single-vector retrieval misses relevant passages that share specific terms with the query, and a cross-encoder over a large shortlist is too slow for your latency budget. For small corpora, a single-vector model plus keyword search plus an optional cross-encoder is simpler to operate and usually good enough. As always, measure on your own labelled queries before committing to the extra storage and tooling.
