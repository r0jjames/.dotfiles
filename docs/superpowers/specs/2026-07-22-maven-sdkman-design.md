# Maven via SDKMAN — Design

Date: 2026-07-22
Status: Approved

## Problem

`lib/tools/maven.py` installs Maven via `brew_install("maven")`. Brew's
`maven` formula depends on `openjdk`, whose formula pulls ~19 unrelated
libraries on macOS (cairo, harfbuzz, fontconfig, libX11, libxcb, webp,
little-cms2, ...) — a Linux-oriented dependency chain applied regardless of
platform. Eclipse Temurin's native macOS JDK builds need none of that; they
use macOS's own font/graphics APIs.

## Decision

Switch `maven.py` to install both Maven and its JDK through **SDKMAN**,
bootstrapping SDKMAN itself if absent. Brew is dropped for this tool
entirely (no `brew=()`/`casks=()` on the `Tool`).

Pinned versions:
- Java: `21.0.5-tem` (Temurin 21, current LTS)
- Maven: latest available via `sdk install maven` (SDKMAN's default)

## Components

`lib/tools/maven.py`:
- `_ensure_sdkman()` — installs SDKMAN via its official
  `curl -s "https://get.sdkman.io" | bash` installer, only if
  `~/.sdkman/bin/sdkman-init.sh` is missing. Runs once, ever.
- `_sdk(cmd)` — runs an `sdk` subcommand via
  `bash -c 'source ~/.sdkman/bin/sdkman-init.sh && <cmd>'`, since `sdk` is a
  shell function (not a binary on PATH) and can't be invoked like `brew`.
- `post_install` — ensures SDKMAN, then installs Java 21.0.5-tem and Maven,
  each skipped if `~/.sdkman/candidates/{java,maven}/current` already exists
  (mirrors `brew_install`'s already-installed skip).
- `status_probe` — checks `~/.sdkman/candidates/maven/current` exists.
  (Can't use `core.have("mvn")`: SDKMAN's PATH shim only exists inside a
  shell that has sourced its init script, not in this Python process's
  environment.)
- `extra_uninstall` — prints a skip message; SDKMAN candidates are left
  installed, consistent with how brew packages are left installed elsewhere
  in this repo on `uninstall`.

## Shell integration side-effect

SDKMAN's installer auto-appends its own init block to `~/.zshrc` on first
run. Since `~/.zshrc` is a symlink into this repo (`zsh/.zshrc`), that edit
lands in the tracked file. This is expected and should be committed after
the first real run — the init snippet is SDKMAN-prescribed and not
hand-written here, since getting it subtly wrong breaks the `sdk` command
and `JAVA_HOME` resolution.

## Migration

The brew-installed `maven` (and `openjdk`, if nothing else depends on it)
from the prior brew-based install get uninstalled as part of this change,
so the machine ends up with exactly one Maven/JDK, sourced via SDKMAN.

## Testing

- `install.py install maven` — confirm `~/.sdkman/candidates/maven/current`
  and `.../java/current` exist afterward.
- Fresh shell — confirm `mvn -v` reports the Temurin JDK, not Homebrew's.
- `install.py status` — confirm `maven` reports `installed`.
