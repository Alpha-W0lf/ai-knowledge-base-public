# Cross-encoder reranking of a fused shortlist

A cross-encoder reads the query and one candidate passage together, as a single input sequence, and outputs one relevance score. Because every token of the query can attend to every token of the passage, it captures interactions that a vector comparison misses: negation, which entity a pronoun refers to, whether the passage answers the question or merely mentions its words.

The cost is that nothing can be precomputed. Each (query, passage) pair is a full forward pass through the model. Scoring a million documents per query is out of the question, so a cross-encoder always sits behind a cheaper first stage. The usual pattern is: retrieve a shortlist of 20 to 100 candidates with hybrid search, score each pair with the cross-encoder, and keep the top 5 to 10.

## Choosing the shortlist size

The shortlist size N trades recall against latency. A small model such as MiniLM-L6 trained on MS MARCO scores a few hundred short pairs per second on a laptop CPU, so N = 30 adds tens of milliseconds, while N = 200 adds noticeable delay. If the right passage is not in the shortlist, the reranker cannot rescue it, so measure first-stage recall at N before blaming the reranker.

## Degrading safely

Rerankers fail in production: the model file is missing, the GPU is busy, an input is too long, or a dependency upgrade breaks loading. A robust retriever treats the reranker as optional. If it raises, return the fused order unchanged and label the response so callers know reranking did not run. Silent fallbacks hide outages, so log every fallback and count them.

## Does it help?

Cross-encoders usually lift precision at the top of the list on question-style queries, but the size of the lift depends on the domain. On a small, clean corpus where the first stage already puts the right document first, there is nothing left to improve, and a measured result of "no lift" is common. That outcome is a property of the test set as much as of the model. Decide whether to turn reranking on by default from a held-out measurement with confidence intervals, not from general reputation.
