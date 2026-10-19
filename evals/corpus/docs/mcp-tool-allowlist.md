# Read-only tool allowlists for MCP servers

A Model Context Protocol (MCP) server exposes tools that an AI agent can call. Every tool is a capability handed to a model that may be confused, manipulated or simply wrong. The safest default is a short, explicit allowlist of tools that only read data, with anything that writes or deletes kept out of the default configuration.

## Allowlist, do not denylist

Register tools from an explicit list of names. A denylist that hides a few dangerous tools fails open: a new tool added next month is exposed automatically. An allowlist fails closed: a new tool is invisible until someone adds it deliberately, which forces a review.

## Separate profiles

Keep tools that modify state, such as adding a data source, triggering a sync or deleting records, behind a separate profile that must be turned on explicitly, for example with an environment variable. The default profile, the one a new user or a public demo gets, should contain only read tools. Test both profiles: assert that the default profile registers exactly the allowlisted names and that write tools appear only when the private profile is enabled.

## Tool annotations

The MCP specification lets a server attach annotations to each tool, including readOnlyHint, destructiveHint, idempotentHint and openWorldHint. Clients can use them to decide when to ask the user for confirmation; a client might auto-approve read-only tools and prompt for destructive ones. Annotations are hints from the server, not guarantees, so clients should not trust annotations from untrusted servers. For your own server, set them accurately and test that every public tool advertises readOnlyHint = true.

## Make "read-only" true

A tool marked read-only must not write anywhere: no cache files, no index rebuilds, no log files inside the data directory, no network calls that change state. Hidden writes are easy to introduce, for example a search function that rebuilds an index if it seems stale. Test it directly: snapshot the data directory, call the tool many times, and assert that nothing changed.

## Bound the inputs

Even read tools can be abused through their arguments. Cap result counts, date ranges and query lengths, and validate types before doing any work.
