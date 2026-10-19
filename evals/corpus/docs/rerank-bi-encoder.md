# Bi-encoders: embedding queries and documents separately

A bi-encoder maps the query and each document to a vector independently, using the same or two related encoders. Relevance is the similarity between the two vectors, usually cosine similarity or a dot product. Because document vectors do not depend on the query, they can be computed once at indexing time and stored in an approximate nearest neighbour index. At query time only the query is encoded, which takes a few milliseconds.

This is the architecture behind dense retrieval: sentence-transformer models, nomic-embed-text, E5 and many others. It is what makes semantic search over millions of passages practical.

## What a bi-encoder cannot see

Compressing a whole passage into one vector loses detail. The model has to decide in advance what the passage is about, without knowing the question. Fine distinctions suffer: "how to disable caching" and "how to enable caching" can land very close together, and so can two product versions that differ by one number. Rare identifiers, error codes and names are often handled poorly, which is one reason hybrid systems pair the vector leg with keyword search.

## Training signal

Bi-encoders are trained with contrastive objectives. Each training query has a positive passage and a set of negatives, and the loss pushes the query vector toward the positive and away from the negatives. In-batch negatives, where the other positives in the batch serve as negatives, are cheap but easy. Mined hard negatives, passages that look relevant but are not, teach the model the distinctions that matter most and give the largest gains.

## Bi-encoder versus reranker

The two are complementary rather than competing. The bi-encoder is the fast recall stage that narrows millions of documents to a shortlist. A cross-encoder reranker is the slow precision stage that orders that shortlist by reading each pair jointly. If you can only afford one, the bi-encoder plus keyword search is the usual choice, because a reranker without a good first stage has nothing to rerank.

When you upgrade the bi-encoder model, every stored vector must be recomputed, since vectors from different models live in different spaces. Track the model name and dimension alongside the index so that a mixed index is refused rather than silently searched.
