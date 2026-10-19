# BM25 scoring and its two parameters

BM25 is the default ranking function of most full-text search engines, including Lucene, Elasticsearch, OpenSearch and Tantivy. It scores a document for a query by adding up a contribution from each query term. Each contribution combines how rare the term is across the collection (inverse document frequency) with how often it appears in the document (term frequency), adjusted for document length.

## Term frequency saturation: k1

In a naive model, a document that mentions a term twenty times scores twenty times higher than one that mentions it once. BM25 saturates instead: each extra occurrence adds less than the previous one. The parameter k1 controls how fast saturation happens. With k1 = 0, term frequency is ignored entirely and only presence matters. With large k1, frequency keeps counting for a long time. The common default is k1 = 1.2, with sensible values between about 0.5 and 2.0.

## Length normalisation: b

Long documents contain more words, so they match more terms by chance. The parameter b controls how strongly scores are normalised by document length relative to the average length in the collection. b = 1 applies full normalisation; b = 0 disables it. The default b = 0.75 suits most prose. Collections of very uniform length are insensitive to b, while collections that mix short notes with long reports can benefit from tuning it.

## Tuning on your own data

The defaults are good, and many teams never change them. If you do tune, use a labelled dev set, sweep a small grid, and confirm the winner on held-out queries; gains are usually a few points of nDCG at most. Changes upstream in tokenisation or stemming matter more than k1 and b.

## Strengths

BM25 needs no training, handles rare terms and exact identifiers extremely well, and explains itself: you can see which terms matched and how much each contributed. It is weak when the query and the document use different words for the same idea, which is the gap that dense vector search fills. That complementarity is the core argument for hybrid search.

Note that BM25 ignores word order and negation: a query containing "not X" still rewards documents that mention X.
