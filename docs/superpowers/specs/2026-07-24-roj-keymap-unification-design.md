# roj-keymap unification + rename

## Problem

The existing `Roj-Ffree` custom IntelliJ keymap unifies only the F1-F12
actions across macOS and Windows (identical Ctrl/Alt/Shift chords, never
Cmd/Win, per `intellij/README.md`). Every other everyday action (navigation,
edit, refactor, run/debug) still uses each OS's native chord, and those
frequently use a genuinely different key — not just a Cmd-vs-Ctrl swap — on
Mac vs Windows (e.g. Go to Class is `Cmd+O` on Mac, `Ctrl+N` on Windows).
Since the user works in IntelliJ on both a personal Mac and a work/VDI
Windows box, this means memorizing two shortcuts per action instead of one.

Separately, the installed keymap's name/file (`Roj-Ffree`) should become
`roj-keymap`.

## Goals

1. Rename the installed keymap identifier from `Roj-Ffree` to `roj-keymap`
   everywhere it's the actual keymap name/filename (not the descriptive
   "F-free" concept in comments/docs).
2. Extend the existing "identical Ctrl/Alt/Shift-only chord on both OSes"
   design to the everyday actions documented in README's Part 2 cheatsheet,
   for the subset where Mac and Windows genuinely differ (not just a
   Cmd&harr;Ctrl modifier swap).

## Non-goals

- Not remapping actions where Mac/Windows already share the same key and
  differ only by the expected Cmd&harr;Ctrl (or Cmd&harr;Alt for tool-window
  digits) convention — e.g. Find Action, Recent Files, Reformat Code,
  Duplicate Line, Project/VCS tool-window digits. These stay native.
- Not attempting to unify IntelliJ's full action set (thousands of actions).
  Scope is bounded to the ~16 actions identified below.

## Scope: actions to unify

Identified by diffing README's Part 2 table against the real bundled
IntelliJ CE keymap XML (`$default.xml`, `Mac OS X 10.5+.xml`, extracted from
`app-client.jar`) — not guessed from memory. Every entry below genuinely
differs between OS (different letter/key, or is F-row on one side):

| Action ID | Mac (current) | Windows (current) | New unified chord |
|---|---|---|---|
| `Run` | `control R` | `shift F10` (F-row) | **hot:** `Ctrl+Alt+W` |
| `Debug` | `control D` | `shift F9` (F-row) | **hot:** `Ctrl+Alt+X` |
| `Back` | `meta OPEN_BRACKET` / `meta alt LEFT` | `control alt LEFT` | **hot:** `Ctrl+Alt+Left` |
| `Forward` | `meta CLOSE_BRACKET` / `meta alt RIGHT` | `control alt RIGHT` | **hot:** `Ctrl+Alt+Right` |
| `GotoClass` | `meta O` | `control N` | leader: `;` `Shift+C` |
| `GotoFile` | `meta shift O` | `control shift N` | leader: `;` `F` |
| `GotoSymbol` | `meta alt O` | `control shift alt N` | leader: `;` `Y` |
| `EditorDeleteLine` | `meta BACK_SPACE` | `control Y` | leader: `;` `Backspace` |
| `EditorSelectWord` (Extend Selection) | `alt UP` | `control W` | leader: `;` `Up` |
| `EditorUnSelectWord` (Shrink Selection) | `alt DOWN` | `control shift W` | leader: `;` `Down` |
| `Generate` | `meta N` | `alt INSERT` | leader: `;` `G` |
| `Refactorings.QuickListPopupAction` (Refactor This) | `control T` | `control alt shift T` | leader: `;` `Q` |
| `SelectNextOccurrence` (Multi-cursor next occurrence) | `control G` | `alt J` | leader: `;` `V` |
| `ChooseRunConfiguration` (Run chooser) | `control alt R` (**currently unbound** — see Known regression below) | `alt shift F10` (F-row) | leader: `;` `Shift+W` |
| `ChooseDebugConfiguration` (Debug chooser) | `control alt D` (**currently unbound**) | `alt shift F9` (F-row) | leader: `;` `Shift+X` |
| `HideAllWindows` | `control shift F12` (inherited, F-row) | `control shift F12` (F-row) | leader: `;` `J` |

`Run`/`Debug` get the two genuinely-free hot-set letters (`W`, `X` — verified
against every `control alt <letter>` binding in bundled `$default.xml` and
both Mac keymap files) since they're the highest-frequency actions in scope.
`Back`/`Forward` get `Ctrl+Alt+Left/Right`: Windows already binds exactly
that in `$default.xml`, so only the Mac side needs an override. Everything
else goes in the leader set (`Ctrl+Alt+;` then a key) — structurally
collision-free against all bundled defaults (no stock action uses a
semicolon-prefixed two-key chord), so no alphabet pressure there. Letter
picks in the leader set avoid every second-keystroke already used by the
existing F-row leader entries (documented in README Part 1).

### Known regression this also fixes

`ChooseRunConfiguration`/`ChooseDebugConfiguration` are currently fully
unbound on Mac (empty `<action id="X"/>`) as a side effect of freeing
`Ctrl+Alt+R`/`Ctrl+Alt+D` for `RenameElement`/`ToggleLineBreakpoint`,
per the existing `KNOWN_CONFLICTS` list — meaning Mac currently has **no
keyboard shortcut at all** for these two actions. Giving them a leader-set
home restores keyboard access and keeps both OSes identical, rather than
leaving Mac permanently degraded.

### New collision found: `ResizeToolWindowLeft`/`Right`

`Mac OS X 10.5+.xml` binds `ctrl+alt+Left`/`ctrl+alt+Right` to
`ResizeToolWindowLeft`/`ResizeToolWindowRight` (Windows' `$default.xml` has
no such override, so Windows needs no change here). Adopting
`Ctrl+Alt+Left/Right` for `Back`/`Forward` requires unbinding these two on
the **Mac file only**, via the established empty `<action id="X"/>` idiom.

## Rename

- `<keymap name="Roj-Ffree" ...>` &rarr; `<keymap name="roj-keymap" ...>` in
  both `intellij/keymap-macos.xml` and `intellij/keymap-windows.xml`.
- Installed filename `Roj-Ffree.xml` &rarr; `roj-keymap.xml`
  (`_KEYMAP_TARGET` in `lib/tools/intellij.py`).
- `README.md`, `vdi-apply-keymap.ps1`: every reference to selecting/finding
  the keymap by name updates to `roj-keymap`.
- Code comments describing the *concept* ("F-free keymap", "Roj F-free
  keymap (Windows / Linux / VDI)") are left as-is — only the actual
  identifier changes.
- Test `test_keymap_name_is_roj_ffree` renames to
  `test_keymap_name_is_roj_keymap` and asserts `"roj-keymap"`.

## Migration cleanup

Because `_KEYMAP_TARGET` changes, `_post()`/`_uninstall()` in
`lib/tools/intellij.py` must also remove any stale `Roj-Ffree.xml` left over
from a prior install in every config dir — otherwise both the old and new
keymap show up in IntelliJ's Settings &rarr; Keymap dropdown after an
upgrade. `_post()` deletes a stale `Roj-Ffree.xml` (if present) alongside
installing `roj-keymap.xml`; `_probe()`'s installed-check is unaffected
(it already only checks the new target name).

## Docs

- README Part 1 ("Custom F-free overrides") gains the 16 new rows above.
- README Part 2 loses the rows that moved into Part 1, keeping only the
  genuinely-native (modifier-swap-only) entries.
- The "Verifying conflicts" section gains the `ResizeToolWindowLeft/Right`
  collision and the `ChooseRunConfiguration`/`ChooseDebugConfiguration`
  un-regression to its running list, consistent with how the original 7
  F-row conflicts are documented.

## Tests

Existing `tests/test_intellij.py` structural tests (well-formed XML, no
F-keys survive, every action has a chord, Mac/Windows bindings identical,
no duplicate chord per file, unbind hygiene, keymap name) apply unchanged to
the larger action set — no new test *shapes* needed, just more data through
the same assertions. `KNOWN_CONFLICTS` gains the two new
`ResizeToolWindowLeft`/`ResizeToolWindowRight` (mac-only) entries.

## Verification

`./install.py install intellij` on this Mac (already has IntelliJ CE
installed) re-links `roj-keymap.xml`, confirms the stale `Roj-Ffree.xml` is
removed, and `python -m pytest tests/test_intellij.py` (or `unittest`) passes.
Manual in-IDE check of a few relocated chords (Rename still works, new
`Ctrl+Alt+W` runs, `Ctrl+Alt+;` `F` opens Go to File) is left to the user
since it requires the IDE UI.
