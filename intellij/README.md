# intellij — IntelliJ IDEA Community + F-free cross-OS keymap

Installs IntelliJ IDEA Community (macOS) and a **custom keymap that uses no
F1-F12 keys**, identical on macOS and Windows, so shortcuts behave the same on
your personal Mac, your work Windows laptop, and the Citrix Windows VDI —
without depending on the F-row (which the NuPhy Win/Mac switch and Citrix
mangle). See [`../citrix-vdi/README.md`](../citrix-vdi/README.md) for the
F-row hardware story; those Karabiner rules stay in place for other apps.

## Why F-free

The custom keymap `Roj-Ffree` redeclares every action IntelliJ maps to F1-F12
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

> **Settings → Keymap → dropdown → `Roj-Ffree`** → Apply.

Then glance down the list for any red **conflict** marks and adjust if your
plugins claim one of the chords (see [Verifying](#verifying-conflicts)).

## VS Code muscle-memory layer (optional)

You asked for a VS Code feel too. `plugins.txt` lists the **VSCode Keymap**
plugin (`com.intellij.plugins.vscodekeymap`). It's usually bundled — enable it
in **Settings → Plugins**, then it appears as another entry in the Keymap
dropdown. `Roj-Ffree` does **not** depend on it; it's a separate switchable
keymap, not a base.

## The VDI (Citrix Windows) — how the keymap gets there

Dotfiles can't reach into the VDI (separate Windows host). Two ways in:

### Path A — Settings Sync (recommended, automatic)

Keymaps sync **per-OS**, and both your work laptop and the VDI are Windows, so:

1. **Work laptop:** Settings → Settings Sync → enable, scoped to **Keymap**
   only (avoids syncing unrelated settings between laptop and VDI).
2. **VDI:** sign into the **same JetBrains account**.

The `Roj-Ffree` keymap (and its active selection) lands in the VDI on its own.
Keep your **personal Mac off Settings Sync** — dotfiles handles the Mac, and
Mac↔Windows keymaps don't sync anyway (different modifiers).

### Path B — one-shot script (fallback / instant seed)

If you'd rather not use account sync, run [`vdi-apply-keymap.ps1`](vdi-apply-keymap.ps1)
**inside the VDI** (close IntelliJ first):

```powershell
powershell -ExecutionPolicy Bypass -File .\vdi-apply-keymap.ps1
```

It downloads `keymap-windows.xml`, drops it into every IntelliJ config dir,
then tells you to pick `Roj-Ffree` in Settings → Keymap. The dotfiles repo is
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

## Part 2 — Standard everyday shortcuts (unchanged defaults)

These are IntelliJ defaults, kept as-is. `⌘`=Cmd, `⌥`=Option/Alt, `⌃`=Ctrl, `⇧`=Shift.

### Search / navigate

| Action | macOS | Windows |
|---|---|---|
| Search Everywhere | `⇧⇧` (double Shift) | `Shift Shift` |
| Find Action | `⌘⇧A` | `Ctrl+Shift+A` |
| Go to Class | `⌘O` | `Ctrl+N` |
| Go to File | `⌘⇧O` | `Ctrl+Shift+N` |
| Go to Symbol | `⌘⌥O` | `Ctrl+Alt+Shift+N` |
| Recent Files | `⌘E` | `Ctrl+E` |
| Go to Declaration | `⌘B` | `Ctrl+B` |
| Go to Implementation | `⌘⌥B` | `Ctrl+Alt+B` |
| Back / Forward | `⌘[` / `⌘]` | `Ctrl+Alt+←` / `→` |
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
| Delete Line | `⌘⌫` | `Ctrl+Y` |
| Comment Line | `⌘/` | `Ctrl+/` |
| Move Line Up / Down | `⌥⇧↑` / `↓` | `Alt+Shift+↑` / `↓` |
| Extend / Shrink Selection | `⌥↑` / `⌥↓` | `Ctrl+W` / `Ctrl+Shift+W` |
| Multi-cursor (next occurrence) | `⌃G` | `Alt+J` |
| Generate | `⌘N` | `Alt+Insert` |
| Surround With | `⌘⌥T` | `Ctrl+Alt+T` |

### Refactor (non-F defaults)

| Action | macOS | Windows |
|---|---|---|
| Refactor This | `⌃T` | `Ctrl+Alt+Shift+T` |
| Extract Variable | `⌘⌥V` | `Ctrl+Alt+V` |
| Extract Method | `⌘⌥M` | `Ctrl+Alt+M` |
| Extract Field | `⌘⌥F` | `Ctrl+Alt+F` |
| Inline | `⌘⌥N` | `Ctrl+Alt+N` |

### Run / debug (non-F defaults; F-based ones are in Part 1)

| Action | macOS | Windows |
|---|---|---|
| Run | `⌃R` | `Shift+F10` → *rebind if needed* |
| Debug | `⌃D` | `Shift+F9` → *rebind if needed* |
| Run… (chooser) | `⌃⌥R` | `Alt+Shift+F10` |

> Note: `Run`/`Debug` on Windows default to `Shift+F10`/`Shift+F9`. They're not
> in the Part-1 list because on macOS they're `⌃R`/`⌃D` (no F-key). If the
> Windows F-based Run/Debug bother you, add them to the keymap the same way —
> suggested: `Ctrl+Alt+;` `Enter` (run) / `Ctrl+Alt+;` `Shift+Enter` (debug).

### Tool windows

| Action | macOS | Windows |
|---|---|---|
| Project | `⌘1` | `Alt+1` |
| Version Control | `⌘9` | `Alt+9` |
| Hide all tool windows | `⌘⇧F12` → *see Part 1 note* | `Ctrl+Shift+F12` |

## Verifying conflicts

Found on 2026-07-24: 4 of the 7 hot-set chords collided with pre-existing
IntelliJ default bindings (verified against the bundled `Mac OS X 10.5+.xml`
/ `$default.xml`), which is why **Rename silently did nothing** — it tied
with `ChooseRunConfiguration`. Both XML files now carry `remove="true"`
entries that free those chords (see the bottom of each file); a test
(`test_known_inherited_conflicts_are_removed`) guards against regressing
this. If IntelliJ resaves the file after you edit the keymap in-app, re-check
for new red conflict markers — a future IDE version could reclaim a freed
chord:

1. Settings → Keymap → type an action name (e.g. "Step Over").
2. Conflicting bindings show a red marker. Right-click the *other* action →
   **Remove Shortcut**, then mirror the fix as a `remove="true"` entry in
   both `keymap-macos.xml` and `keymap-windows.xml` (only add it to
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
together. The OS-specific `remove="true"` blocks are allowed to differ.

## Uninstall

```sh
./install.py uninstall intellij
```

Removes the keymap file from every config dir. The IntelliJ app is left
installed (remove via `brew uninstall --cask intellij-idea-ce` or Finder). If
`Roj-Ffree` is still selected, switch back to a default keymap in Settings →
Keymap.
