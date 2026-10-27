# feder-skills

feder-skills is a public Claude Code plugin and marketplace of five slash-command skills: `/full-picture`, `/compare-states`, `/options-analysis`, `/explain-simply` and `/greenfield`. They shape how Claude reasons about a problem and presents the result, for anyone who uses Claude Code on real codebases. Each skill is a `skills/<name>/SKILL.md`; there is no code and no test suite, and a change is checked by running the skill in a session.

<!-- >>> git-workflow (generated block; do not edit by hand) -->
## Git workflow

- `main` changes only through a PR, squash-merged.
<!-- <<< git-workflow -->

## Project state

- 2026-10-07: not launched — no release yet. Retires at the first version tag.
- 2026-10-07: the project holds no user data; a skill runs inside the user's own Claude Code session and writes only to their machine. Retires if it ever stores or sends data off the user's machine.
