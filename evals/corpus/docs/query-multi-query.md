# Multi-query rewriting and query expansion

A single phrasing of a question may miss relevant documents that use different words. Multi-query rewriting asks a language model to produce several alternative versions of the user's query, runs retrieval for each one, and merges the result lists. The merge is usually a rank-based fusion, such as reciprocal rank fusion, which rewards documents that several rewrites agree on.

A question like "why is my search slow" might be rewritten as "search latency causes", "vector index query performance" and "reduce retrieval response time". Each rewrite reaches a slightly different region of the corpus, and together they recall more relevant documents than the original alone.

## Classic query expansion

Before language models, query expansion added related terms automatically. Pseudo-relevance feedback, in the style of the Rocchio algorithm or RM3, retrieves with the original query, assumes the top few results are relevant, extracts frequent distinctive terms from them, and adds those terms to the query for a second retrieval pass. It needs no model, but it can drift badly when the first-pass results are off-topic, reinforcing the wrong interpretation.

Synonym dictionaries and acronym expansion are simpler still and work well in domains with stable vocabularies, such as expanding "k8s" to "kubernetes".

## Costs

Multi-query rewriting multiplies retrieval work by the number of rewrites and adds a language model call. Latency can be contained by running the retrievals in parallel. Rewrites can also introduce interpretations the user did not intend, so the original query should always be one of the variants.

## Decomposition

A related technique splits a complex question into sub-questions, such as "compare the memory use of HNSW and IVF-PQ" into one question about each index. Each sub-question is retrieved separately, and the passages are combined for the answer. This helps multi-part questions where no single document covers everything.

## Measure recall first

The main benefit of rewriting is recall, so measure recall at the shortlist size with and without rewriting on labelled queries. Check precision at the top too, because extra variants can pull in loosely related documents.
