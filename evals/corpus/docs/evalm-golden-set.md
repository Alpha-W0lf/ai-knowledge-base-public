# Building a golden query set with hard negatives

A golden set is a collection of queries with known correct results, used to measure retrieval quality repeatably. A good one is the single most valuable asset in a retrieval project: it turns every design debate into a measurement.

## Sources of queries

Real user queries are best, sampled across topics and difficulty, with personal data removed. When the system is new, write queries the way users would, not the way the documents are written. Queries copied from document titles or that reuse a passage's exact wording make keyword search look perfect and measure very little.

Mix query types: short keyword lookups, natural-language questions, queries that use synonyms or describe a concept without naming it, and queries about exact identifiers or error strings.

## Hard negatives

A hard negative is a document that looks relevant but is not. Build the corpus so that each topic has close neighbours: documents that share vocabulary and subject matter but answer a different question. A query about merging ranked lists without comparable scores should rank the document about rank-based fusion above the one about score normalisation, even though both discuss fusion.

Phrase hard queries by intent. A query that names the wrong concept explicitly, such as "rank fusion, not score summing", rewards keyword matching on the word it says to avoid, because keyword search ignores negation. Describe the need instead and let the system find the right document.

## Labels

Use graded labels: 2 for documents that answer the query, 1 for related documents, 0 otherwise. Have a second person label a sample and measure agreement; disagreement shows where the guidelines are unclear.

## Size and corpus design

The corpus must be large enough that retrieval is hard. If the system returns half the corpus for every query, almost any order contains the right document, and the metrics hit a ceiling that hides real differences. Dozens of documents of realistic length, split into several chunks each, and around a hundred queries are a reasonable minimum for a small domain. Always report a random baseline beside the system's numbers so readers can see how far above chance it is.
