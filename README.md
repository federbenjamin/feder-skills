# feder-skills

Six skills for [Claude Code](https://code.claude.com) that shape how Claude reasons and explains. One plugin; each skill runs as `/<name>`.

## Install

```
claude plugin marketplace add federbenjamin/feder-skills
claude plugin install feder-skills@feder-skills
```

## Skills

| Skill | What it does |
| --- | --- |
| `/full-picture` | Maps a system, an issue, or a decision as one rendered page: the parts, how they connect, what changes over time, what the change touches. |
| `/compare-states` | One self-contained page that sets two or more states of the same mechanism side by side. |
| `/options-analysis` | Lays out the options for a decision with the trade-off that decides each, recommendation first. |
| `/explain-simply` | Explains a thing as if the reader has never seen the work: what it is, what is wrong or changing, why it matters. |
| `/greenfield` | Designs as if the repo's rules did not exist, then adjudicates the clean design against them to find rules that have outlived their reason. |
| `/afk` | Unattended mode: works through everything queued without stopping, banks the questions only a human can answer, and ends with a handoff. |

Skills that render a page use `SendUserFile` when it exists and name the file's path otherwise.

## License

MIT
