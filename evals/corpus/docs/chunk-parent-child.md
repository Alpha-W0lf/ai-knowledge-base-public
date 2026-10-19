# Parent-child retrieval: search small chunks, return large ones

Parent-child retrieval, sometimes called small-to-big retrieval, separates the unit you search from the unit you return. Documents are split twice: into large parent chunks of a page or a section, and into small child chunks of a few sentences inside each parent. Only the children are embedded and indexed. When a child matches a query, the system returns its parent instead.

The small children make matching sharp, because each vector describes one narrow idea. The large parents give the reader or the language model enough surrounding context to use the match: the definitions, caveats and steps around the sentence that matched.

## Variants

A sentence-window variant indexes single sentences and returns the matched sentence plus a few sentences on either side. Another variant indexes summaries or hypothetical questions generated for each parent, and returns the parent text. In every variant the index stores a pointer from each child to its parent, and the retriever resolves the pointers after ranking.

## Deduplication and budgets

Several children from the same parent often match one query. Without care, the same parent is returned three times and fills the context window with repeated text. Group matches by parent, keep the best-scoring child's rank for ordering, and return each parent once. Because parents are large, set the number of returned parents from a token budget rather than a fixed count.

## Trade-offs

The index is larger, because every child needs its own vector, and ingest is more complex, because two levels of splitting must stay consistent when a document changes. Citations need thought too: the user sees the parent, but the evidence was a specific child, so highlighting the child inside the parent helps people verify the answer.

Parent-child retrieval is most useful when answers need context that a small chunk cannot hold, such as procedures with many steps. If a single mid-sized chunk already contains complete answers, the extra machinery adds little. Compare against plain chunking on the same queries before adopting it.
