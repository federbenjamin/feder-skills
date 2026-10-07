# feder-skills

<p align="center"><strong>Six Claude Code skills that shape how Claude reasons and explains.</strong></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/federbenjamin/feder-skills" alt="License"></a>
</p>

feder-skills is a plugin for [Claude Code](https://code.claude.com). It adds six slash commands that change how Claude thinks through a problem and how it presents the result: a rendered map of a system, two states side by side, a decision laid out by its deciding trade-off, a plain explanation, a design freed from the repo's rules, and an unattended working mode. It is for anyone who uses Claude Code on real codebases and wants its reasoning on the page, not only in the answer.

## Install

Needs [Claude Code](https://code.claude.com) with plugins. One command adds the marketplace and installs the plugin:

```
claude plugin install feder-skills --marketplace federbenjamin/feder-skills
```

## Features

- **`/full-picture`.** Maps a system, an issue, or a decision as one rendered page: the parts, how they connect, what changes over time, what the change touches.
- **`/compare-states`.** One self-contained page that sets two or more states of the same mechanism side by side.
- **`/options-analysis`.** Lays out the options for a decision with the trade-off that decides each, recommendation first.
- **`/explain-simply`.** Explains a thing as if the reader has never seen the work: what it is, what is wrong or changing, why it matters.
- **`/greenfield`.** Designs as if the repo's rules did not exist, then adjudicates the clean design against them to find rules that have outlived their reason.
- **`/afk`.** Unattended mode: works through everything queued without stopping, banks the questions only a human can answer, and ends with a handoff.

## Usage

Each skill runs as `/<name>` in a Claude Code session, with what you want it applied to after it:

```
/full-picture the checkout flow
/options-analysis where the session cache should live
/explain-simply this PR
/afk
```

Skills that render a page (`/full-picture`, `/compare-states`) use `SendUserFile` when it exists and name the file's path otherwise. Each skill's full instructions are its `skills/<name>/SKILL.md`.

## Contributing

Report a problem in [issues](https://github.com/federbenjamin/feder-skills/issues). PRs are welcome; see [CONTRIBUTING](https://github.com/federbenjamin/.github/blob/main/CONTRIBUTING.md) and [SECURITY](https://github.com/federbenjamin/.github/blob/main/SECURITY.md). There is no test suite: a change to a skill is checked by running it in a session.

## License

MIT © Benjamin Feder
