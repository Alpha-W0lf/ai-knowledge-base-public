# Metadata filtering: pre-filter versus post-filter

Real retrieval queries often come with constraints beyond the text: only documents from one channel, only items newer than a date, only content the user is allowed to see. Metadata filtering applies those constraints, and where in the pipeline it happens matters a great deal.

## Post-filtering

Post-filtering runs the vector or keyword search first, takes the top k results, and then discards those that fail the filter. It is easy to implement on top of any index. The problem is that a selective filter can remove most or all of the top k. If only two percent of documents match the filter, a top-50 search returns about one matching result on average, even though many matching documents exist further down. The common workaround, fetching far more candidates before filtering, costs latency and still fails for very selective filters.

## Pre-filtering

Pre-filtering applies the filter first and searches only among matching documents. Results are correct, with k matches whenever k exist. For exact scans this is straightforward. For approximate graph indexes it is harder, because removing nodes can disconnect the graph and strand the search. Engines handle this with filter-aware traversal, separate indexes per common filter value, or a switch to an exact scan when the filter matches few rows.

## Access control is a filter that must not fail

Permission filters are not a relevance feature; they are a security boundary. Apply them as a pre-filter, or enforce them in the storage layer, so that a document the user may not see is never scored, returned, cached or passed to a model. Post-filtering permissions risks leaks through side channels, such as result counts, timing or a cache shared across users.

## Filtered evaluation

Test retrieval quality under realistic filters, not only on the full corpus. A system that scores well unfiltered can collapse when a common filter is applied, especially with post-filtering. Include a few filtered queries in the evaluation set and check that the number of returned results matches what the corpus actually contains.

## Date filters and freshness

Date filters are the most common constraint in news-like content. Store dates in a sortable format, such as ISO 8601, and make sure every document has one, because documents with missing dates silently disappear from filtered results.
