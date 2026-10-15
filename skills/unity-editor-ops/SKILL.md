---
name: unity-editor-ops
description: >-
  Operate a running Unity editor through the Unity CLI to change and test a project live:
  reach the editor, change scenes and code, recompile, run tests, ride play mode and read
  numbers out of it, and recover from the failure modes that stall an editor driven by an agent
  (Safe Mode, a throttled unfocused editor, a blocked main thread, stale import workers, a
  cursor lock, a full disk). Use together with the unity-cli skill whenever an agent must make
  or verify a change in a Unity project on this machine. NO-GO: project-specific tuning and
  gameplay judgment, which belong to the project's own rules and brief.
---

# unity-editor-ops

The `unity-cli` skill (Unity's own, from the `unity` plugin) documents every command. This skill
is the operating discipline around it, learned from runs that lost hours to each item below. Read
the project's `AGENTS.md` and `docs/rules/unity.md` before the first command; they outrank this.

## Reach the editor

Find out whether an editor is up, which one, and whether it can take commands, before touching
anything: `unity status --until-ready --project-path <absolute project path>` is the one call that
answers all three. Always pass the project's full path, so a sibling worktree's editor never
answers for yours, and never drive an editor whose project is not your checkout.

When status finds nothing, find out why in this order: the Pipeline package missing from the
project (`unity pipeline list`; install it, then the editor needs a package resolve), Safe Mode
from compile errors (fix the errors in the files, then the editor restarts), an editor still
importing, a sandbox hiding it. A missing editor is opened with `unity open <project>` and waited
for with `--until-ready`; a lock file left by a killed editor (`Temp/UnityLockfile`) and orphaned
`AssetImportWorker` processes from the old editor are cleared first.

## Make a change

Prefer the Pipeline's own commands (scene, GameObject, component, asset, package) over `eval`, and
`eval` over editing a scene file by hand; scene YAML edited on disk under an open editor is the
last resort and needs a refresh afterwards. After any script edit, `unity recompile` and read its
errors before going on. A new tool the project will need more than once becomes a `[CliCommand]`
in its editor assembly, discovered through `unity list`, rather than a script pasted into `eval`
every time.

`eval` runs on the editor's main thread. Nothing inside it may wait on an asynchronous editor
API (a test run, a build, an import, a package operation): that blocks the thread the result
travels on and deadlocks the editor until it is killed. Start such work with `--detach` and follow
it with `unity job wait`, or use the command the Pipeline already has for it (`run_tests`,
`build`, `package_*`, each with a `_status` partner).

Statics survive play-mode transitions when the project disables domain reload, so a handler
registered from `eval` keeps running after play stops; remove what you register. A player setting
touched from code (`Application.runInBackground` is the usual one) is written into
`ProjectSettings` and shows up in `git status`; put it back when the run ends.

## Ride play mode and trust what you read

The editor throttles its update loop when it is not the frontmost window, which is the normal
state for an agent; a game can then sit at frame 1 while status says "playing", and timers padded
to compensate make every test take six times longer than it should. The recipe that removes the
problem, in this order: `set_autotick` once per editor session, `editor_set_run_in_background` for
the session (and off again at the end), `editor_play`, `status --until-ready` (the Pipeline server
drops out during the reload), then `wait_for` on `Time.frameCount` with `op: changed` before any
number is read. A screenshot (`capture_game_view`) is a look, not proof; the frame counter is.

Drive the game the way its input layer expects: set the project's input component fields, or
`simulate_key` / `simulate_pointer`, from a registered per-frame sampler rather than one-off
calls, and log each sample as one tagged line. Read the console (`unity command console`) before
`editor_stop`: a project with "clear on play" wipes it at the next entry, and the editor's own
`Logs/Editor.log` keeps what the console lost. After the ride, stop, wait for ready, reopen the
scene you started from, and never save a sample or third-party scene a ride dirtied.

Cursor lock: character controllers from Unity's starter assets lock and hide the mouse whenever
the editor gains focus in play mode, so a person at the machine sees the pointer vanish and cannot
click; Esc releases it, stopping play ends it. Say so in the report when a run leaves the editor
in play mode for the operator.

## Tests

The Edit-mode suite runs against the open editor with `unity test --mode EditMode --project-path
<absolute path> --output <xml>`; the NUnit XML is the result, not the console. Batch mode
(`unity run` or `Unity -batchmode -runTests`) only with the editor closed: two editors on one
`Library` corrupt it. Never copy a project to run its tests elsewhere; the copy costs gigabytes
on a disk that is usually near full and tests code the editor is not running.

## Leave it as you found it

Before the report: play mode off, the project's scene open and not dirty, temporary scripts and
their `.meta` files removed together, player settings restored, no `eval`-registered handlers
left, and `unity status` ready. The report carries the numbers from captured output, names what
was and was not verified, and says exactly what the editor state is for whoever sits down next.
