# Writing repository guidance files for coding agents

A guidance file is a markdown document at the root of a repository that coding agents load at the start of every session. AGENTS.md is a widely adopted name; some tools use their own file name and can import AGENTS.md so that one file serves every agent. The file tells the agent what it cannot discover quickly by itself: the exact commands, the definition of done, the design rules and where deeper documentation lives.

## Keep it short

Everything in the file costs context on every request, and a long file buries the rules that matter. Aim for well under 200 lines. For each line, ask whether removing it would cause the agent to make a mistake. If not, cut it. Research on context files has found that long, generic files add cost without improving task success.

## Say what to do

Phrase rules positively: "run the formatter before committing" rather than a list of things never to do. Prohibitions tend to make the banned behaviour more salient. Avoid long lists of bad examples; the model may treat them as a menu. Convey the intent behind a rule so the agent can apply it to cases the file does not mention.

## Commands and done

List the exact commands for installing, linting, testing a single file, running the whole suite and running the evaluation, with their flags. Define what done means concretely: tests pass, lint is clean, a bug fix includes a test that fails without it, and claims in the pull request are marked as verified or not.

## Point, do not copy

Link to deeper documents with a short trigger that says when to read them: "read docs/ARCHITECTURE.md when you change retrieval or the MCP surface." Do not paste architecture overviews or file-by-file tours into the guidance file; they go stale and cost context for little benefit.

## Enforce what must hold

Rules that must never be broken belong in CI checks, hooks or permission settings, where they are enforced, not only in prose. The guidance file can mention that the check exists so the agent understands why a failure happened.

Treat the file like code: review changes to it and prune rules that no longer change behaviour.
