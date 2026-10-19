# Tokenization, stemming and stop words in keyword search

Before a full-text engine can match anything, it has to turn text into terms. This analysis chain runs on documents at index time and on queries at search time, and the two must match exactly, or terms that look identical to a person never meet in the index.

## Tokenizers

A tokenizer splits text into tokens. A simple tokenizer splits on whitespace and punctuation and lowercases everything. That breaks identifiers: "gpt-4o-mini", "user_id" and "v2.3.1" become several fragments, and a search for the full identifier may match documents that only contain the fragments. Engines offer alternatives, such as keeping tokens with internal punctuation or indexing both the whole token and its parts. Code search and log search usually need custom tokenization.

Languages without spaces between words, such as Chinese and Japanese, need dictionary-based or n-gram tokenizers, and mixed-language collections need per-field or per-document language detection.

## Stemming and lemmatisation

Stemming strips suffixes so that "indexing", "indexed" and "indexes" all become "index". The Porter and Snowball stemmers are common rule-based choices. Stemming raises recall but can merge words with different meanings; "university" and "universe" collapse to the same stem in some stemmers. Lemmatisation uses a dictionary to map words to their base form more accurately, at higher cost.

## Stop words

Stop words are very common words like "the", "of" and "is". Removing them shrinks the index and speeds up queries. But removing them breaks phrase queries and some meaningful queries: "to be or not to be" vanishes entirely, and "The Who" becomes "who". Because BM25 already gives common words very low weight through inverse document frequency, many modern setups keep stop words in the index.

## Keep the chain consistent

Changing the analysis chain changes which terms exist in the index, so it requires a full reindex. Record the analyzer configuration next to the index, and rerun the retrieval evaluation after any change. A new stemmer can move metrics more than any amount of BM25 parameter tuning.
