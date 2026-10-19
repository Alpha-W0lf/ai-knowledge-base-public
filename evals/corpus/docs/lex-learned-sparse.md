# Learned sparse retrieval with SPLADE

Learned sparse retrieval keeps the inverted index of keyword search but lets a neural model decide which terms describe a document and how much each one weighs. SPLADE, introduced by Formal and colleagues in 2021, is the best-known model of this kind.

SPLADE runs a transformer masked-language-model head over the text and produces a weight for every term in the model's vocabulary. A regularisation term during training pushes most weights to zero, so each document ends up with a few hundred non-zero terms. Crucially, those terms include words that never appear in the text: a passage about "car repair" can receive weight for "vehicle" and "mechanic". This is called term expansion.

## Why it is attractive

The output is a sparse vector over a vocabulary, which fits directly into an inverted index. Existing search engines can serve it with little change, matching is still term-based and explainable, and expansion closes much of the vocabulary gap that plain BM25 suffers from. On public benchmarks SPLADE models are competitive with dense retrievers and often generalise better to new domains.

## Costs

Documents must be encoded by a transformer at index time, which is far slower than building a BM25 index. Queries must be encoded too, unless a query-side variant is used that skips the model and uses plain tokens. Expanded documents also have more terms, so posting lists grow and queries can be slower than BM25 without careful pruning of low weights.

## Relationship to the other legs

Learned sparse retrieval sits between BM25 and dense vectors. It keeps exact term matching for identifiers, adds learned expansion for synonyms, and remains an inverted-index method rather than a nearest neighbour search. Some systems use three legs, BM25, learned sparse and dense, fused with a rank-based method. Each extra leg adds latency and operational weight, so measure whether it improves your held-out metrics enough to justify it before adopting it.
