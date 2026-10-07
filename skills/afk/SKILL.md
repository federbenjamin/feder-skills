---
name: afk
argument-hint: "[optional priorities or notes before leaving]"
description: The human is leaving — switch to unattended mode and keep working through everything queued without stopping. Use when the user says "/afk", "I'm leaving", "going afk", "heading out — keep going", "keep working while I'm gone", or otherwise hands off the queued work to continue without them, and stay in this mode until they return.
---

The human is away. Work through everything queued in this session without stopping — no "shall I proceed?", no waiting for confirmation on reversible steps. All standing rules (git safety, approval flows, secrets posture) still apply; unattended mode changes pacing, never permissions.

The run ends only when the queue is exhausted (§Ending the run). Until then, keep working: a status note, a summary, or a finished milestone goes in the same message as the next tool call. When every item left waits on background work, arm a watch on it and pause; its exit wakes you and the run goes on.

## Deciding

Deciding is the default. A reversible step, anything a rule file, plan, ticket, or the code itself answers, and any near-tie are yours to call — take it, record one line in the bank's Decisions section, keep going.

Bank a question only for a meaningful product decision that the plan, the code, the rules, the tickets, and everything else in the repo cannot resolve. Never stall the whole run on one — park that branch and continue.

**One root, one question.** Blocked items sharing an unknown are ONE entry naming every item that waits on it.

Bank to a file immediately (long runs compact; in-conversation questions get lost). Use `afk-questions.md` in the folder your instructions name for docs written for the user (else `docs/afk/` in the repo), two sections:

```markdown
# Decisions
- <what you chose> — <why, one line>

# Open questions

## Q1 — <short title>
- Context: what was being done, why it blocked
- Question: the decision needed
- Recommendation: your answer and why
- Parked: what work waits on this
```

If later work resolves an open question, move it to Decisions with the answer.

## Ending the run

When the queue is exhausted — every item done, blocked, or parked — two final steps, in this order:

1. **Write a handoff doc** (`/handoff` when you have it; otherwise a markdown file beside the bank file: what was done, what is parked and why, the next step), mission = the parked work. It cites the bank file path, so the returning human or a post-compaction session has both. This is the run's durable record; the chat log is not.
2. **Stop every shell you started.** Kill each background process still running — dev servers, watchers, tails, long polls. An unattended run leaves nothing burning behind it. If one genuinely must survive, say which and why. Shells are the only thing you remove: a file the run made and the repo cannot keep (a test-only agent definition, a hook, an index) is moved to the same agent-docs folder as the handoff, never deleted.

Then stop: a final message of the handoff path, the shells you killed, and nothing else.

## When the human returns

Any new human message ends unattended mode. The handoff doc and the bank file are the record — point at both, answer what they ask, and resume parked work as answers arrive.
