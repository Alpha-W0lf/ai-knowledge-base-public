# Embedding model versioning and full index rebuilds

Vectors produced by different embedding models live in different spaces. A vector from one model compared with a vector from another produces a number, but the number means nothing. The same is true, more subtly, for two versions of the same model, for the same model at a different output dimension, and sometimes for the same model served by a different runtime with a different tokenizer or pooling setting.

The consequence is simple: every vector in an index must come from exactly one model configuration, and queries must be embedded with that same configuration.

## Stamp every row

Store a version stamp with each chunk, such as "nomic-embed-text@768", and record the same stamp in the code that embeds queries. At query time, check that the index stamp matches the runtime stamp, and refuse to search if it does not. A refusal with a clear message ("index built with model A, runtime expects model B; rebuild the index") is far better than results that look plausible and are quietly wrong.

Stamps should include anything that changes the vector: model name, model revision or digest, output dimension, and any prefix the model expects, such as "search_query:" and "search_document:" task prefixes used by some embedding families.

## Rebuild, do not patch

When the model changes, re-embed every document from the source files. Mixing old and new vectors during a gradual migration produces an index in which some documents are effectively invisible. If downtime matters, build the new index beside the old one, run the evaluation suite against it, and switch the read path in one step once it passes.

Keep source documents as the system of record. The vector index is derived data; it should always be possible to delete it and rebuild it from files with one command. Teams that treat the index as primary storage end up unable to change models at all.

## Re-evaluate after every rebuild

A new model changes rankings everywhere. Rerun the retrieval evaluation on the dev and held-out sets after the rebuild and compare against the last committed results. Score distributions shift too, which matters if any downstream step uses fixed score thresholds or weighted score fusion.
