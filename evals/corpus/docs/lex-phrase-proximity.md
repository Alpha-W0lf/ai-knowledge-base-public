# Phrase and proximity queries

A plain keyword query treats the query as a bag of terms: a document that contains "rate" in one paragraph and "limit" in another scores almost as well as one that contains the exact phrase "rate limit". Phrase and proximity queries use term positions to tell these apart.

## Positional indexes

To support phrases, the index stores not just which documents contain a term but the positions where it occurs. A phrase query for "rate limit" then matches only documents in which "limit" appears at the position right after "rate". Storing positions makes the index larger, often by half or more, so some engines let you disable positions on fields that never need phrase search.

## Slop and proximity

A proximity query, sometimes written with a slop value, allows the terms to be up to n positions apart, possibly in a different order. "rate limit"~3 matches "limit the rate" and "rate of the limit". Some scoring functions add a proximity bonus automatically: documents where the query terms appear close together get a higher score, even without an explicit phrase operator.

## When users need it

Phrase matching matters for names, titles, error messages and multi-word technical terms whose meaning depends on word order, such as "cache miss" versus "miss cache", or "Python data model" versus a passage that merely mentions Python and data. Error messages copied from logs are a classic case: users paste them whole and expect the document containing that exact string.

## Phrases and hybrid search

Vector search captures topical similarity but has no concept of exact adjacency, so it cannot enforce a phrase. In a hybrid system, quoted phrases can be routed to the keyword leg as true phrase queries while the vector leg receives the unquoted text. Many query parsers also boost exact phrase matches automatically, which helps long natural-language queries without any user syntax.

## Costs

Phrase queries are slower than term queries, because the engine must intersect position lists, not just document lists. Very common terms make this expensive. Engines mitigate it with techniques such as indexing common two-word combinations as single terms, sometimes called shingles or common-grams.
