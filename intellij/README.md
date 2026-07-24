# intellij — IntelliJ IDEA Community + F-free cross-OS keymap

Installs IntelliJ IDEA Community (macOS) and a **custom keymap that uses no
F1-F12 keys**, identical on macOS and Windows, so shortcuts behave the same on
your personal Mac, your work Windows laptop, and the Citrix Windows VDI —
without depending on the F-row (which the NuPhy Win/Mac switch and Citrix
mangle). See [`../citrix-vdi/README.md`](../citrix-vdi/README.md) for the
F-row hardware story; those Karabiner rules stay in place for other apps.

## Why F-free

The custom keymap `roj-keymap` redeclares every action IntelliJ maps to F1-F12
onto **Ctrl / Alt / Shift chords only** (never Cmd/Win). Benefits:

- Same physical keys on Mac and Windows → one muscle memory everywhere.
- Ctrl/Alt/Shift pass cleanly through Citrix **Scancode** input mode.
- Unaffected by the `citrix-vdi` Karabiner *Left-Cmd → Alt* rule (we avoid Cmd).
- No reliance on the F-row at all — the mode-switch / brightness-key problem
  disappears for IntelliJ.

## Install

### macOS (personal) — *run on: Mac*

```sh
./install.py install intellij
```

Installs the `intellij-idea-ce` cask (if missing), then **symlinks**
`keymap-macos.xml` into every `~/Library/Application Support/JetBrains/IdeaIC*/keymaps/`.

### Work Windows laptop — *run from: Git Bash*

```sh
./install.py install intellij
```

IntelliJ itself is assumed already installed on the Windows host. This
**copies** `keymap-windows.xml` into every
`%APPDATA%\JetBrains\{IntelliJIdea*,IdeaIC*}\keymaps\` (symlinks need admin).

> **If it says "No IntelliJ config dir":** the IDE has never launched, so its
> version-stamped config folder doesn't exist yet. Open IntelliJ once, then
> re-run `./install.py install intellij`.

### Activate it (one time, every install)

Dropping the file makes the keymap **available**, not active. In IntelliJ:

> **Settings → Keymap → dropdown → `roj-keymap`** → Apply.

Then glance down the list for any red **conflict** marks and adjust if your
plugins claim one of the chords (see [Verifying](#verifying-conflicts)).

## VS Code muscle-memory layer (optional)

You asked for a VS Code feel too. `plugins.txt` lists the **VSCode Keymap**
plugin (`com.intellij.plugins.vscodekeymap`). It's usually bundled — enable it
in **Settings → Plugins**, then it appears as another entry in the Keymap
dropdown. `roj-keymap` does **not** depend on it; it's a separate switchable
keymap, not a base.

## The VDI (Citrix Windows) — how the keymap gets there

Dotfiles can't reach into the VDI (separate Windows host). Two ways in:

### Path A — Settings Sync (recommended, automatic)

Keymaps sync **per-OS**, and both your work laptop and the VDI are Windows, so:

1. **Work laptop:** Settings → Settings Sync → enable, scoped to **Keymap**
   only (avoids syncing unrelated settings between laptop and VDI).
2. **VDI:** sign into the **same JetBrains account**.

The `roj-keymap` keymap (and its active selection) lands in the VDI on its own.
Keep your **personal Mac off Settings Sync** — dotfiles handles the Mac, and
Mac↔Windows keymaps don't sync anyway (different modifiers).

### Path B — one-shot script (fallback / instant seed)

If you'd rather not use account sync, run [`vdi-apply-keymap.ps1`](vdi-apply-keymap.ps1)
**inside the VDI** (close IntelliJ first):

```powershell
powershell -ExecutionPolicy Bypass -File .\vdi-apply-keymap.ps1
```

It downloads `keymap-windows.xml`, drops it into every IntelliJ config dir,
then tells you to pick `roj-keymap` in Settings → Keymap. The dotfiles repo is
private, so the raw URL needs a public/tokenised link — or copy the XML in by
hand and pass `-LocalPath .\keymap-windows.xml`.

---

# Cheatsheet

## Part 1 — Custom F-free overrides (identical on Mac + Windows)

These replace the old F1-F12 shortcuts. Same chords on every machine.

**Hot set** — single `Ctrl+Alt+<key>`:

| Action | Chord | Was (default) |
|---|---|---|
| Rename | `Ctrl+Alt+R` | ⇧F6 |
| Find Usages | `Ctrl+Alt+U` | ⌥F7 |
| Toggle breakpoint | `Ctrl+Alt+K` | ⌘F8 / Ctrl+F8 |
| Step Over | `Ctrl+Alt+D` | F8 |
| Step Into | `Ctrl+Alt+G` | F7 |
| Step Out | `Ctrl+Alt+Q` | ⇧F8 |
| Evaluate Expression | `Ctrl+Alt+E` | ⌥F8 |

**Leader set** — `Ctrl+Alt+;` then a key:

| Action | Chord | Was |
|---|---|---|
| Resume program | `Ctrl+Alt+;` `R` | F9 |
| Move | `Ctrl+Alt+;` `M` | F6 |
| Change Signature | `Ctrl+Alt+;` `C` | ⌘F6 / Ctrl+F6 |
| Next error | `Ctrl+Alt+;` `E` | F2 |
| Previous error | `Ctrl+Alt+;` `Shift+E` | ⇧F2 |
| File Structure popup | `Ctrl+Alt+;` `S` | ⌘F12 / Ctrl+F12 |
| Jump to Last Tool Window | `Ctrl+Alt+;` `W` | F12 |
| Terminal | `Ctrl+Alt+;` `T` | ⌥F12 / Alt+F12 |
| Toggle Bookmark | `Ctrl+Alt+;` `B` | F3 / F11 |
| Show Bookmarks | `Ctrl+Alt+;` `Shift+B` | ⌘F3 / ⇧F11 |
| Build Project | `Ctrl+Alt+;` `K` | ⌘F9 / Ctrl+F9 |
| Stop | `Ctrl+Alt+;` `X` | ⌘F2 / Ctrl+F2 |
| Run to Cursor | `Ctrl+Alt+;` `U` | ⌥F9 / Alt+F9 |
| Quick Documentation | `Ctrl+Alt+;` `D` | F1 (mac) |
| Show Execution Point | `Ctrl+Alt+;` `P` | ⌥F10 / Alt+F10 |
| Select In | `Ctrl+Alt+;` `I` | ⌥F1 / Alt+F1 |
| Next Difference (diff) | `Ctrl+Alt+;` `N` | F7 |
| Previous Difference | `Ctrl+Alt+;` `Shift+N` | ⇧F7 |
| Open Source in New Window | `Ctrl+Alt+;` `O` | ⇧F4 |
| Smart Step Into | `Ctrl+Alt+;` `A` | ⇧F7 |
| Show Error Description | `Ctrl+Alt+;` `Shift+D` | ⌘F1 / Ctrl+F1 |
| Go to Class | `Ctrl+Alt+;` `Shift+C` | ⌘O (mac) / Ctrl+N (win) |
| Go to File | `Ctrl+Alt+;` `F` | ⌘⇧O (mac) / Ctrl+Shift+N (win) |
| Go to Symbol | `Ctrl+Alt+;` `Y` | ⌘⌥O (mac) / Ctrl+Alt+Shift+N (win) |
| Delete Line | `Ctrl+Alt+;` `Backspace` | ⌘⌫ (mac) / Ctrl+Y (win) |
| Extend Selection | `Ctrl+Alt+;` `↑` | ⌥↑ (mac) / Ctrl+W (win) |
| Shrink Selection | `Ctrl+Alt+;` `↓` | ⌥↓ (mac) / Ctrl+Shift+W (win) |
| Generate | `Ctrl+Alt+;` `G` | ⌘N (mac) / Alt+Insert (win) |
| Refactor This | `Ctrl+Alt+;` `Q` | ⌃T (mac) / Ctrl+Alt+Shift+T (win) |
| Run… (chooser) | `Ctrl+Alt+;` `Shift+W` | ⌃⌥R (mac) / Alt+Shift+F10 (win) |
| Debug… (chooser) | `Ctrl+Alt+;` `Shift+X` | ⌃⌥D (mac) / Alt+Shift+F9 (win) |
| Hide All Tool Windows | `Ctrl+Alt+;` `J` | ⌘⇧F12 / Ctrl+Shift+F12 |
| Multi-cursor (next occurrence) | `Ctrl+Alt+;` `V` | ⌃G (mac) / Alt+J (win) |

**Also promoted to the hot set** (highest-frequency actions, single chord —
these differed by more than a Cmd↔Ctrl swap between Mac and Windows, so they
moved here instead of staying native):

| Action | Chord | Was |
|---|---|---|
| Run | `Ctrl+Alt+W` | ⌃R (mac) / Shift+F10 (win) |
| Debug | `Ctrl+Alt+X` | ⌃D (mac) / Shift+F9 (win) |
| Back | `Ctrl+Alt+←` | ⌘[ (mac) / Ctrl+Alt+← (win, unchanged) |
| Forward | `Ctrl+Alt+→` | ⌘] (mac) / Ctrl+Alt+→ (win, unchanged) |

## Part 2 — Standard everyday shortcuts (unchanged defaults)

These are IntelliJ defaults, kept as-is. `⌘`=Cmd, `⌥`=Option/Alt, `⌃`=Ctrl, `⇧`=Shift.

### Search / navigate

| Action | macOS | Windows |
|---|---|---|
| Search Everywhere | `⇧⇧` (double Shift) | `Shift Shift` |
| Find Action | `⌘⇧A` | `Ctrl+Shift+A` |
| Recent Files | `⌘E` | `Ctrl+E` |
| Go to Declaration | `⌘B` | `Ctrl+B` |
| Go to Implementation | `⌘⌥B` | `Ctrl+Alt+B` |
| Find in Files | `⌘⇧F` | `Ctrl+Shift+F` |
| Find / Replace | `⌘F` / `⌘R` | `Ctrl+F` / `Ctrl+R` |

### Edit / code

| Action | macOS | Windows |
|---|---|---|
| Show Intentions / quick-fix | `⌥⏎` | `Alt+Enter` |
| Code Completion | `⌃Space` | `Ctrl+Space` |
| Reformat Code | `⌘⌥L` | `Ctrl+Alt+L` |
| Optimize Imports | `⌃⌥O` | `Ctrl+Alt+O` |
| Duplicate Line | `⌘D` | `Ctrl+D` |
| Comment Line | `⌘/` | `Ctrl+/` |
| Move Line Up / Down | `⌥⇧↑` / `↓` | `Alt+Shift+↑` / `↓` |
| Surround With | `⌘⌥T` | `Ctrl+Alt+T` |

### Refactor (non-F defaults)

| Action | macOS | Windows |
|---|---|---|
| Extract Variable | `⌘⌥V` | `Ctrl+Alt+V` |
| Extract Method | `⌘⌥M` | `Ctrl+Alt+M` |
| Extract Field | `⌘⌥F` | `Ctrl+Alt+F` |
| Inline | `⌘⌥N` | `Ctrl+Alt+N` |

### Tool windows

| Action | macOS | Windows |
|---|---|---|
| Project | `⌘1` | `Alt+1` |
| Version Control | `⌘9` | `Alt+9` |

## Verifying conflicts

Found on 2026-07-24: 4 of the 7 hot-set chords collided with pre-existing
IntelliJ default bindings (verified against the bundled `Mac OS X 10.5+.xml`
/ `$default.xml`, and against `KeymapImpl`'s actual bytecode), which is why
**Rename silently did nothing** — it tied with `ChooseRunConfiguration`.

**The fix is an empty, self-closing `<action id="X"/>` tag — not a
`remove="true"` attribute.** JetBrains' own docs describe `remove="true"` for
a *different* XML dialect (plugin.xml action registration); the keymap
scheme-file reader (`keymaps/*.xml`, what these files are) never checks for
it — an early attempt using `remove="true"` here was silently ignored and
IntelliJ resaved the file with the shortcut re-added as a plain duplicate.
The real mechanism, confirmed by decompiling `KeymapImpl.readExternal` /
`getShortcutList`: each `<action id="X">` element in a keymap file **replaces**
that id's entire shortcut list for this keymap, and if the element has zero
`<keyboard-shortcut>` children the list is empty — which `getShortcutList`
returns as-is, without falling back to the parent keymap. The bundled `Mac OS
X 10.5+.xml` itself uses this exact idiom (17 empty `<action id="X"/>` tags).
Both our XML files now carry these at the bottom; tests
(`test_known_inherited_conflicts_are_unbound`, `test_unbound_actions_carry_no_shortcut`)
guard against regressing this. If IntelliJ resaves the file after you edit
the keymap in-app, re-check for new red conflict markers — a future IDE
version could reclaim a freed chord:

1. Settings → Keymap → type an action name (e.g. "Step Over").
2. Conflicting bindings show a red marker. Right-click the *other* action →
   **Remove Shortcut**, then mirror the fix as an empty `<action id="TheOtherAction"/>`
   tag in both `keymap-macos.xml` and `keymap-windows.xml` (only add it to
   `keymap-macos.xml` too if the conflict is mac-only, e.g. it comes from
   `Mac OS X 10.5+.xml` rather than `$default.xml`) so both machines and the
   cheatsheet stay in sync.

**After editing a keymap XML by hand:** close IntelliJ first — it overwrites
the file with its own copy on exit, discarding hand-edits made while it was
running. Re-open, and if the same keymap was already active it reloads your
changes.

Because both `keymap-macos.xml` and `keymap-windows.xml` carry **identical**
relocated chords (a test enforces this, case-insensitively — IntelliJ itself
may re-save the file in lowercase), fix a relocated chord in both files
together. The OS-specific empty-action unbind entries are allowed to differ
(mac needs 2 extra: conflicts that come from `Mac OS X 10.5+.xml` itself,
which Windows never inherits).

**Second pass (unifying everyday actions, same day):** adopting
`Ctrl+Alt+Left`/`Right` for `Back`/`Forward` collided with
`ResizeToolWindowLeft`/`ResizeToolWindowRight`, which `Mac OS X 10.5+.xml`
binds to the same chord — Windows' `$default.xml` has no such binding, so
that unbind is mac-only, same idiom as above. Separately,
`ChooseRunConfiguration`/`ChooseDebugConfiguration` had been sitting fully
unbound on Mac since the first pass (freed to make room for
`Rename`/`ToggleLineBreakpoint`) — they now get a real leader-set chord
instead of staying dead, restoring keyboard access to them on Mac rather
than leaving that regression in place.

## Uninstall

```sh
./install.py uninstall intellij
```

Removes the keymap file from every config dir. The IntelliJ app is left
installed (remove via `brew uninstall --cask intellij-idea-ce` or Finder). If
`roj-keymap` is still selected, switch back to a default keymap in Settings →
Keymap.
