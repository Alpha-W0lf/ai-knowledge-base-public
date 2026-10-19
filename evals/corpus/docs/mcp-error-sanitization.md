# Sanitising error messages in agent-facing tools

When a tool fails, the error message goes back to the model, and often from there into a chat transcript, a log aggregator or a user's screen. Raw exception text frequently contains details that should not leave the server: absolute file paths that reveal user names and directory layout, hostnames, database connection strings, environment variable values, and stack traces that show library versions.

## What to strip

Replace absolute filesystem paths with a placeholder such as "[path]". Remove anything that looks like a credential, token or connection URL. Drop stack traces from public responses entirely and log them server-side instead. Truncate very long messages, since a multi-kilobyte error can also crowd the model's context.

A regular expression that matches path-like strings beginning with a slash or a drive letter catches most path leaks. Test it with realistic messages from your own stack, including paths inside quotes and paths at the start of a line.

## Keep errors useful

Sanitising should not turn every failure into "an error occurred". The model needs enough information to recover or to explain the problem to the user. Return a stable error code, such as empty_index, embedding_version_mismatch or fts_unavailable, plus a short human-readable message that says what to do next: "No documents in the knowledge base. Run ingest first." Codes let the agent branch on the failure type without parsing prose.

## Fail closed, visibly

A tool that cannot do its job properly should return an error, not a degraded result dressed up as success. If a hybrid search cannot run its keyword leg, returning vector-only results with no indication misleads the caller. Either fail with a clear code, or return the degraded result with an explicit field saying what was skipped, and log it.

## Where to sanitise

Sanitise at the boundary, in the tool handler that builds the response, not deep inside library code. Internal code should keep full details for logs and debugging. One sanitising function used by every public handler is easier to test and audit than ad hoc cleanup in each tool.
