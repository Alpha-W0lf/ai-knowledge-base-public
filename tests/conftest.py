"""
Tests run on the offline stub embedder unless AI_KB_EMBEDDINGS is already set, and
with the cross-encoder off unless AI_KB_CE is set (tests that need it pass an adapter).

Set AI_KB_EMBEDDINGS=ollama (with Ollama and nomic-embed-text running) to run the
same ingest and search tests against the real model.
"""

import os

os.environ.setdefault("AI_KB_EMBEDDINGS", "stub")
os.environ.setdefault("AI_KB_CE", "0")
