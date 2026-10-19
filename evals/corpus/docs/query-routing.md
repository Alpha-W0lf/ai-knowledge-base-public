# Query routing and intent classification

Not every query should take the same path. A routing step looks at the incoming query and decides where to send it: which index, which retrieval mode, which tool, or whether retrieval is needed at all. Routing lets one system handle lookups, open questions, structured queries and small talk without forcing all of them through one pipeline.

## Common routing decisions

Index selection sends a query to the collection that can answer it, such as API reference, internal policies or support tickets. Mode selection chooses keyword-heavy retrieval for queries with identifiers and error codes, and dense retrieval for conceptual questions. Tool selection sends questions about live data, such as "how many open tickets do I have", to an API or a SQL query instead of a document index. A no-retrieval route answers greetings and simple follow-ups directly.

## How to build a router

Rules come first: regular expressions for ticket ids or version numbers, keyword lists for specific products. They are fast, explainable and easy to test. A small classifier trained on labelled queries handles fuzzier categories. A language model with a prompt describing each route is the most flexible option and the slowest; it is often used to bootstrap labels for a cheaper classifier later.

## Fail safely

Routers make mistakes. A query misrouted to the wrong index returns confident, irrelevant results. Mitigations include routing to several destinations when confidence is low and fusing the results, adding a fallback route that searches everything, and returning which route was taken in the response so that errors can be traced.

## Evaluate the router separately

Measure routing accuracy on its own labelled set, with a confusion matrix showing which routes get mixed up. Then measure end-to-end retrieval quality with the router in place. A router that is 95 percent accurate can still hurt overall quality if its errors fall on the most important queries, so look at the cost of each kind of mistake, not just the average accuracy.
