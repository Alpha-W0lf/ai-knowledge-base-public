# Prompt caching for long, repeated context

Prompt caching is a feature offered by several model providers that reuses the model's computation for a prompt prefix that has been seen recently. When many requests start with the same long block, such as a system prompt, a set of tool definitions or a large reference document, the provider can store the processed prefix and skip recomputing it. Cached input tokens are billed at a steep discount and the time to first token drops.

Unlike a semantic cache, prompt caching never changes the answer. The model still generates a fresh response for every request; only the work of reading the shared prefix is reused.

## Structure prompts for cache hits

Caching matches on an exact prefix, so order matters. Put stable content first: system instructions, tool definitions, long documents. Put content that changes on every request, such as the user's question, the current time or a request id, at the end. A timestamp placed at the top of the system prompt silently disables caching for everything after it.

Some providers cache automatically; others require marking cache breakpoints explicitly in the request. Caches expire after a few minutes of inactivity in most offerings, sometimes with an option for a longer lifetime at a higher write cost, so caching pays off for bursts of related requests, such as a multi-turn agent session.

## Retrieval-augmented prompts

In retrieval-augmented generation, the retrieved passages differ for each query, which limits caching. Two patterns help. First, keep the instructions and tool definitions in a fixed prefix so at least that part is cached. Second, in a conversation, append new passages after the earlier turns rather than rebuilding the prompt from scratch, so the earlier turns remain a cacheable prefix.

## Measure the effect

Providers report cached and uncached input tokens in each response's usage data. Log those numbers per request and track the cache hit ratio. A sudden drop usually means something started changing near the top of the prompt, such as a reordered tool list or a dynamic value inserted into the system prompt.
