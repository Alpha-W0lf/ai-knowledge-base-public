# Permission rules and approval modes for agents

Coding agents can read files, edit code, run shell commands and call external services. Permission settings decide which of those actions run automatically, which need the user's approval, and which are refused outright. Getting this right is the difference between an agent that is pleasant to use and one that is either constantly interrupting or quietly dangerous.

## Allow, ask, deny

Most tools support three tiers. Allowed actions run without prompting: reading files in the project, running the test suite, listing directories. Ask-first actions pause for approval: installing packages, pushing to a remote, editing files outside the project. Denied actions are refused even if the model requests them: reading secret files, running destructive commands, contacting unknown hosts.

Rules usually match on the tool and a pattern, such as a command prefix or a file path glob. Prefer narrow allow rules, like a specific test command, over broad ones like any shell command.

## Modes

Agents often offer session-wide modes on top of the rules. A planning or read-only mode lets the agent explore and propose changes without editing anything, which is useful for unfamiliar codebases. An accept-edits mode auto-approves file edits but still asks before shell commands. Fully autonomous modes skip prompts and should only run inside a sandbox, such as a container or a disposable virtual machine with no access to credentials.

## Secrets

Keep credentials out of the agent's reach. Store them in one secrets file or a system keychain, deny read access to that location, and inject them into processes through environment variables only where needed. An agent that never sees a token cannot leak it into a log, a commit or a prompt.

## Review the rules like code

Check permission settings into the repository where the tool supports project-level configuration, so the whole team shares one reviewed policy. Watch for approval fatigue: if users click approve on every prompt without reading, the prompts have become noise. Move routine safe actions into the allow list and keep prompts for decisions that genuinely deserve a human look.
