# Delegating to subagents with narrow jobs

Many agent frameworks let a main agent start subagents: separate model sessions with their own context window, instructions and tool set. The main agent hands over a task, the subagent works on it, and only the subagent's final report comes back. Used well, subagents keep the main context clean and let independent work run in parallel.

## Context isolation is the main benefit

A broad code search can read dozens of files. If the main agent does it, all that text sits in its context for the rest of the session, crowding out what matters and raising cost on every later request. A subagent can do the search and return a ten-line summary with file paths. The main agent keeps the conclusion, not the file dumps.

## One narrow job each

Give each subagent a specific role, a defined scope and only the tools it needs. A reviewer subagent gets read-only tools and a checklist; a test-runner subagent gets the shell but not the file editor. "Helpful assistant" personas with every tool are harder to predict and easier to misuse.

Write the brief as if for a capable colleague who has seen nothing: the goal, the relevant paths, constraints, what done looks like, and the exact format of the report. Subagents cannot ask follow-up questions mid-task in most setups, so ambiguity turns into guesswork.

## Fresh eyes for review

A subagent that did not write the code is a better reviewer than the agent that did, because it lacks the author's assumptions. A common pattern is implement, then hand the diff to a fresh reviewer subagent with instructions to look for correctness bugs, missing tests and claims without evidence, then fix what it finds.

## Costs and coordination

Each subagent re-reads whatever context it needs, so many parallel subagents can multiply token usage quickly. Run in parallel only work that is genuinely independent, such as searching different subsystems. Work that edits the same files should stay sequential or use separate branches, or the agents will overwrite each other's changes. And remember that the main agent must verify a subagent's claims before passing them on.
