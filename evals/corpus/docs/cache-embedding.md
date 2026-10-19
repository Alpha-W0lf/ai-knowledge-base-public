# Caching embeddings by content hash

Embedding the same text twice is wasted work. Ingest pipelines re-run often: a scheduled sync picks up a few new documents, a chunking bug is fixed, a source is re-downloaded. Without a cache, each run re-embeds everything, which is slow on a local model and costly on a paid API.

## Key by content, not by path

Compute a hash of the normalised text of each document, or of each chunk, and use it as the cache key together with the embedding model's version stamp. If a file moves to a new folder, its hash is unchanged and nothing is recomputed. If a single word changes, the hash changes and only that document is re-embedded. Keying by file path instead gets both cases wrong: moves trigger needless work and edits under the same path can be missed.

Normalise before hashing: convert line endings, strip trailing whitespace, and apply the same Unicode normalisation that the chunker uses. Otherwise an editor that rewrites line endings causes a full re-embed.

## Idempotent ingest

The same hash makes ingest idempotent. For each source, compare the stored content hash with the new one. Same hash: skip. Different hash: delete that source's old chunks and insert the new ones. This replace-on-change rule keeps the index free of stale chunks, which otherwise linger and get retrieved alongside the current text.

## Include the model in the key

A cached vector is only valid for the model that produced it. Include the model name, revision and output dimension in the cache key or in a stamp stored next to each vector. When the model changes, the cache misses everywhere, which is correct: every document must be re-embedded for the new space.

## Recorded embeddings for tests

The same idea supports reproducible tests. Store vectors for a fixed test corpus and its queries in a file keyed by content hash and model stamp, and let the test suite read them instead of calling the model. Tests then run offline and deterministically, and a missing key should fail loudly rather than fall back to a live model call that hides drift.
