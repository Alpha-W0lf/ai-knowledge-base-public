# Semantic caching of LLM responses

A semantic cache stores previous questions and their answers, and serves a stored answer when a new question means the same thing as an old one. Instead of matching the exact query string, it embeds each incoming query and looks for a cached query whose vector is within a similarity threshold. "How do I reset my password?" and "steps to change a forgotten password" can share one cached answer.

For applications with many repeated questions, such as support assistants and internal help desks, a semantic cache can cut model calls and latency substantially.

## The threshold is the whole game

Set the similarity threshold too low and the cache serves wrong answers: "how do I enable two-factor authentication" and "how do I disable two-factor authentication" are very similar in embedding space but need opposite answers. Set it too high and the cache rarely hits. Tune the threshold on a labelled set of query pairs marked as same-intent or different-intent, and measure false hits separately from missed hits, because a false hit is far more costly than a miss.

## Scope the cache

Answers often depend on more than the question: the user's permissions, their account, the current date, or the documents available. Include those factors in the cache key, or restrict caching to questions whose answers are the same for everyone. A cache that serves one user's private answer to another user is a data leak.

## Invalidation

Cached answers go stale when the underlying documents change. Store, with each entry, the ids and content hashes of the sources it was built from, and evict entries whose sources changed. Add a time-to-live as a backstop for anything you cannot track precisely.

## Measure it like a model

A semantic cache is effectively a classifier deciding "same question or not", so it deserves the same evaluation discipline as any other model: a labelled dev set for tuning the threshold, a held-out set for reporting, and monitoring of hit rate and user corrections in production. Log every cache hit with the matched query and its similarity, so wrong hits can be investigated.
