# MCP read-only allowlist patterns

Public MCP servers should expose an allowlist only: search, discover, and get_status.
Mutation tools such as add_channel and sync_now must stay off the public profile.

Agents calling MCP should never receive absolute owner filepaths in citations.
Use source_id and documented URLs instead. Placeholder for fixture:mcp-allowlist-02.
