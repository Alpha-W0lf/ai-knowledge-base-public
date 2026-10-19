# Fixed-size chunking with overlap

The simplest way to split documents for retrieval is a fixed window: cut the text every N characters or tokens, and start each new chunk a little before the previous one ended. A typical setting is 1,000 to 1,500 characters per chunk with 100 to 200 characters of overlap. The overlap means a sentence that straddles a boundary appears whole in at least one chunk.

Fixed windows are predictable. Every chunk is roughly the same size, which keeps embedding cost and prompt budgets easy to estimate, and the code is a dozen lines. For transcripts and other text without reliable structure, a fixed window is often the most honest choice.

## Picking the size

Chunk size controls what one vector has to represent. Small chunks of a few sentences give precise matches, but each one carries little context, and an answer spread over two paragraphs gets split. Large chunks keep context together but blur the embedding: a 3,000-character chunk about five subtopics matches none of them strongly. Most teams test two or three sizes on a labelled query set and pick the best, rather than reasoning from first principles.

Embedding models also have input limits. Text beyond the model's maximum sequence length is truncated silently by many libraries, so a chunk that is too long loses its tail without any error. Measure chunk length in the model's tokens, not just characters, when you are close to the limit.

## Respecting soft boundaries

A pure character cut can split words and sentences. A small improvement is to accumulate whole paragraphs or sentences until the next one would exceed the limit, and only fall back to a hard word-level cut for a single paragraph that is longer than the window. This keeps chunks readable when they are shown to users as citations.

## Overlap trade-offs

Overlap duplicates text, which inflates the index and can return two near-identical chunks for one query. Deduplicate results by source document, keeping the best chunk, so users do not see the same passage twice. Overlap beyond about 20 percent of the chunk size rarely helps and mostly costs storage and embedding time.
