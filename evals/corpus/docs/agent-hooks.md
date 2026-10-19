# Lifecycle hooks for coding agents

Several coding agents let you register hooks: shell commands that run automatically at fixed points in the agent's lifecycle. Typical hook points are before a tool call runs, after a tool call finishes, when the user submits a prompt, and when the agent stops. The hook receives a description of the event, usually as JSON on standard input, and can allow it, block it with a message, or add context.

## Why hooks instead of instructions

Instructions in a guidance file are advisory. The model reads them and usually follows them, but under a long task or a confusing prompt it can forget or reinterpret them. A hook is deterministic code: it runs every time, whatever the model is thinking. Rules that must always hold belong in hooks, and judgment calls belong in instructions.

Good candidates for hooks include blocking edits to protected files, refusing commands that delete data or rewrite git history, running a formatter after every file edit, and running the test suite before the agent reports that it is done.

## A pre-tool-use example

A hook registered before shell commands can inspect the command string and exit with a blocking status if it matches a dangerous pattern, returning a short explanation that the agent sees. The agent can then choose a safer approach. Because the check is code, it can be unit tested like any other function, including tests for commands that should pass.

## Keep hooks fast and quiet

Hooks run on every matching event, so a slow hook slows the whole session. Keep them to simple checks, and move heavy work such as full test runs to the stop event or to CI. Print nothing on success; a hook that floods the context with output costs tokens on every call.

## Limits

Pattern-matching hooks can be bypassed by unusual command spellings, so treat them as a seatbelt rather than a sandbox. For strong isolation, combine hooks with operating-system sandboxing or permission rules that the agent cannot change. And version the hook scripts in the repository, so that every contributor and every agent session gets the same guardrails.
