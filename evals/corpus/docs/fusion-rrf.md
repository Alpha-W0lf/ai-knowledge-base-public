# Reciprocal rank fusion in a hybrid retriever

Reciprocal rank fusion (RRF) merges the result lists of two or more retrievers using only the position of each item in each list. A document at rank r in one list contributes 1 / (k + r) to its fused score, and the contributions from every list are added. The constant k is usually 60, the value used in the original 2009 paper by Cormack, Clarke and Buettcher. Items are then sorted by the summed score.

The appeal is that RRF never looks at the raw scores. A vector leg returns cosine distances between roughly 0.2 and 0.9, while a BM25 leg returns unbounded positive numbers that depend on document length and corpus statistics. Putting those on one scale is fragile. RRF side-steps the problem: rank 1 is worth the same in every list, whatever produced it.

## How k changes the behaviour

With k = 60, the gap between rank 1 (1/61) and rank 10 (1/70) is small, so a document that appears in both lists at rank 8 beats a document that appears in only one list at rank 1. That is the intended effect: agreement between legs is rewarded more than a single strong opinion. A small k, such as 5, makes the top positions dominate and behaves more like "take the best of each list". Teams rarely need to tune k; the default is robust across collections.

## Implementation notes

Fuse on stable chunk ids, not on text, so that the same chunk reached by both legs is recognised as one item. Fetch more candidates from each leg than you plan to return, for example 60 per leg for a final top 10, because an item that is rank 40 in one list and rank 3 in the other can still finish near the top. Deduplicate by source document after fusion if you want one result per document, keeping the best-ranked chunk.

Ties are common when two items sit at mirrored ranks, such as rank 2 in one list and rank 5 in the other versus the reverse. Break them deterministically, for example by chunk id, so that evaluation runs are reproducible.

## When RRF is the wrong tool

RRF throws away score magnitude. If one leg is far better than the other on your data, equal weighting can drag good results down, and a weighted variant (multiplying each leg's contribution by a weight) or a learned fusion can do better. RRF also cannot recover an item that neither leg retrieved. It is a cheap, strong default for hybrid search, and a good baseline before reaching for anything that needs labelled training data.
