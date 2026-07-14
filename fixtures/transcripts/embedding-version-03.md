# Embedding version and rebuild discipline

Every indexed chunk should store an embedding_version such as nomic-embed-text@768.
If the runtime model or dimension changes, refuse search and ingest until the derived
LanceDB index is rebuilt from durable files.

Think of embedding_version as a schema stamp for vectors: mismatch means stale geometry,
not a soft warning. Placeholder for fixture:embedding-version-03.
