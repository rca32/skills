# Personal Luna worker setup

Enter this branch only when the user explicitly asks to check, install, or
repair the personal `luna_worker` custom agent. This is a user-level Codex
configuration write, not an issue preflight and not implied by installing or
invoking this skill.

The bundled source is [the Luna worker asset](../assets/luna-worker.toml), and
the deterministic installer is
[`configure_luna_worker.py`](../scripts/configure_luna_worker.py). It targets
`${CODEX_HOME:-$HOME/.codex}/agents/luna-worker.toml` without editing
`config.toml`.

## Check and show the diff

Run `check` first. It verifies the reviewed asset digest, reads the installed
Codex version, requires `gpt-5.6-luna` with `max` reasoning in `codex debug
models`, inspects the exact target without following a target symlink, and
returns JSON containing the target kind, status, snapshot, and diff state.

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_luna_worker.py" check
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_luna_worker.py" diff
```

Show the returned diff to the user. `missing` is the normal installable state;
`current` needs no content change. `conflict` means an unsafe mode, different
profile, symlink, hard link, special file, or oversized file occupies the
target. A regular-file conflict has an exact unified diff. Structural conflicts
return `diff=null`, `diff_status=unavailable-target-content-not-read`, and the
target kind instead of pretending the target is absent. Compatibility fields
are deliberately `not-evaluated` for conflicts so an unsafe existing profile
cannot interfere with inspection. Do not install or overwrite a conflict.
Resolve it only under a separate explicit instruction that names the existing
file and desired replacement behavior.

Completion criterion: the user can see the exact target, target kind, and an
exact diff when content was safely read; compatibility checks pass for
installable/current states, and the snapshot belongs to the state being
authorized.

## Install after explicit authorization

Use only the snapshot returned by the immediately preceding `check`:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_luna_worker.py" install \
  --expected-snapshot <snapshot>
```

The installer refuses stale snapshots and conflicting targets, creates only the
`agents` directory when absent, atomically links a mode-`0600` temporary file
into the previously absent target, and reconciles a competing identical install.
It preserves every other Codex file. After readback it runs `codex
--strict-config doctor --json`; a doctor failure leaves the exact installed file
in place, reports `installed-unverified`, and requires diagnosis rather than a
blind retry or deletion.

Run `verify` after installation or when checking an existing installation:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/configure_luna_worker.py" verify
```

Completion criterion: `verify` returns `status=verified`, the target exactly
matches the bundled asset, the installed model catalog contains Luna with max
reasoning, strict doctor reports `config.load=ok`, and no other configuration
file changed. Tell the user to start a new Codex session so agent discovery uses
the installed profile. In that new session, select `luna_worker` for bounded
delegated work matching its description. If discovery or selection is
unavailable, disclose that fact and use another context-isolated worker rather
than silently claiming Luna was used.
