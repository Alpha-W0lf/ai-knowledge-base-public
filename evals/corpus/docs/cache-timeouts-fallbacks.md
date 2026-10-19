# Timeouts, retries and fallbacks in retrieval pipelines

A retrieval pipeline chains several services: an embedding model, a vector store, a keyword index, maybe a reranker and a language model. Each can be slow or unavailable. Without explicit timeouts and fallbacks, one stalled dependency makes the whole request hang.

## Set a timeout on every call

Every network call needs a timeout shorter than the user's patience. Budget the total request time and split it across stages, for example a few hundred milliseconds for the embedding call, similar for each search leg, and a fixed cap for the reranker. A call without a timeout can wait indefinitely when a connection is half-open.

## Retry carefully

Retry only operations that are safe to repeat and errors that are likely to be transient, such as connection resets and rate-limit responses. Use exponential backoff with jitter, cap the number of attempts, and respect any retry-after hint. Retrying a timeout immediately with the same timeout usually just doubles the wait.

## Degrade, and say so

Decide in advance what happens when an optional stage fails. If the reranker times out, return the fused first-stage results. If the keyword index is missing, either fail the hybrid request clearly or fall back to vector search with an explicit flag in the response. The important rule is that a degraded result must be labelled as degraded. Callers, dashboards and evaluations need to know which stages actually ran, or a broken component can stay hidden for weeks.

Fallbacks are rare defences, not normal operation. Log every fallback with the stage, the error type and the latency, count them, and alert when the rate rises. A fallback that fires constantly is an outage that nobody noticed.

## Circuit breakers

When a dependency is down, sending it every request wastes the timeout budget each time. A circuit breaker tracks recent failures and, after a threshold, skips the dependency for a cooling-off period, going straight to the fallback. It periodically lets a trial request through to detect recovery.

## Test the failure paths

Write tests that force each failure: a reranker that raises, a missing index, an embedding call that times out. Assert the exact degraded behaviour and the label in the response.
