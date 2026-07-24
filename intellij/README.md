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

Three tiers, lightest first. Full rationale/verification:
`docs/superpowers/specs/2026-07-24-roj-keymap-two-key-simplification-design.md`.

## Tier 0 — Ctrl-based, already 2-key

| Action | Chord |
|---|---|
| Go to Declaration | `Ctrl+B` |
| Find | `Ctrl+F` |
| Find in Path | `Ctrl+Shift+F` |
| Close tab | `Ctrl+W` |
| Project tool window | `Alt+1` |
| VCS tool window | `Alt+9` |

## Tier 1 — bare `Alt+<key>`, 2-key, high frequency

| Action | Chord |
|---|---|
| Rename | `Alt+R` |
| Find Usages | `Alt+U` |
| Toggle Breakpoint | `Alt+K` |
| Step Over | `Alt+D` |
| Step Into | `Alt+G` |
| Step Out | `Alt+Q` |
| Evaluate Expression | `Alt+E` |
| Run | `Alt+W` |
| Debug | `Alt+X` |
| Go to Class | `Alt+C` |
| Go to File | `Alt+F` |
| Go to Symbol | `Alt+S` |
| Terminal | `Alt+T` |
| Build (CompileDirty) | `Alt+B` |
| Extend Selection | `Alt+↑` |
| Shrink Selection | `Alt+↓` |
| New… (file/class/etc popup) | `Alt+N` |
| Select In (reveal current file) | `Alt+I` |
| Previous Editor Tab | `Alt+[` |
| Next Editor Tab | `Alt+]` |
| Back | `Ctrl+Alt+←` *(kept 3-key — see below)* |
| Forward | `Ctrl+Alt+→` *(kept 3-key — see below)* |

**Why Back/Forward stay 3-key:** bare `Alt+←`/`Alt+→` collides with
`PreviousTab`/`NextTab` (Windows, heavily used) **and**
`EditorPreviousWord`/`EditorNextWord` (Mac — Option+Arrow word navigation,
a fundamental system-wide macOS text-editing convention). Not worth the
regression for a 1-key saving.

**Direct jump-to-tab-N** (the `Cmd+1`..`Cmd+9` browser convention) isn't a
real IntelliJ action — verified against the full bundled action set, only
`NextEditorTab`/`PreviousEditorTab` (cycle one at a time) exist.
`Alt+[`/`Alt+]` above is the closest available substitute.

## Tier 2 — leader, `Alt+Minus` then a key

Lower-frequency actions. Press-release `Alt+Minus`, then press the second
key **alone** (release Alt+Minus first — holding it through the second key
sends the wrong modifier combo and the action won't fire).

| Action | Chord | Action | Chord |
|---|---|---|---|
| Resume program | `Alt+-` `R` | Move | `Alt+-` `M` |
| Change Signature | `Alt+-` `C` | Next error | `Alt+-` `E` |
| Previous error | `Alt+-` `Shift+E` | File Structure popup | `Alt+-` `S` |
| Jump to Last Tool Window | `Alt+-` `W` | Toggle Bookmark | `Alt+-` `B` |
| Show Bookmarks | `Alt+-` `Shift+B` | Stop | `Alt+-` `X` |
| Run to Cursor | `Alt+-` `U` | Quick Documentation | `Alt+-` `D` |
| Show Execution Point | `Alt+-` `P` | Next Difference (diff) | `Alt+-` `N` |
| Previous Difference | `Alt+-` `Shift+N` | Open Source in New Window | `Alt+-` `O` |
| Smart Step Into | `Alt+-` `A` | Show Error Description | `Alt+-` `Shift+D` |
| Delete Line | `Alt+-` `Backspace` | Generate | `Alt+-` `G` |
| Refactor This | `Alt+-` `Q` | Run… (chooser) | `Alt+-` `Shift+W` |
| Debug… (chooser) | `Alt+-` `Shift+X` | Hide All Tool Windows | `Alt+-` `J` |
| Multi-cursor (next occurrence) | `Alt+-` `V` | | |

## Unchanged defaults (already identical, no override needed)

These are IntelliJ defaults, kept as-is — **already the same physical
Ctrl/Alt chord on both OSes out of the box**, no keymap override needed.
(An earlier version of this table showed some of these with `⌘` on macOS;
that was wrong — decompiling the real bundled keymap confirmed macOS
inherits the Ctrl/Alt chord from `$default` unchanged, since neither
`Mac OS X.xml` nor `Mac OS X 10.5+.xml` overrides these actions. `⌥`=Option/Alt,
`⌃`=Ctrl, `⇧`=Shift.)

### Search / navigate

| Action | Chord |
|---|---|
| Search Everywhere | `Shift Shift` (double Shift) |
| Find Action | `Ctrl+Shift+A` |
| Recent Files | `Ctrl+E` |
| Go to Implementation | `Ctrl+Alt+B` |
| Replace | `Ctrl+R` |

### Edit / code

| Action | Chord |
|---|---|
| Show Intentions / quick-fix | `Alt+Enter` |
| Code Completion | `Ctrl+Space` |
| Reformat Code | `Ctrl+Alt+L` |
| Optimize Imports | `Ctrl+Alt+O` |
| Duplicate Line | `Ctrl+D` |
| Comment Line | `Ctrl+/` |
| Move Line Up / Down | `Alt+Shift+↑` / `↓` |
| Surround With | `Ctrl+Alt+T` |

### Refactor (non-F defaults)

| Action | Chord |
|---|---|
| Extract Variable | `Ctrl+Alt+V` |
| Extract Method | `Ctrl+Alt+M` |
| Extract Field | `Ctrl+Alt+F` |
| Inline | `Ctrl+Alt+N` |

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
— each file only unbinds the natives that actually collide with our chords
*in that file's own parent chain* (`Mac OS X.xml`/`Mac OS X 10.5+.xml` vs
`$default.xml`), so the two unbind lists rarely match exactly. `KNOWN_CONFLICTS`
in `tests/test_intellij.py` is the source of truth for which id/chord/OS
combination is expected.

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

**Third pass (2026-07-24, Cmd-vs-Ctrl parity):** re-verified every Part 2 row
against the real bundled `Mac OS X.xml`/`Mac OS X 10.5+.xml` (both extracted
straight from `app-client.jar` — the only jar shipping `keymaps/*.xml`, no
plugin jar contributes more). Only 5 actions genuinely override to Cmd on
Mac (`GotoDeclaration`, `Find`, `FindInPath`,
`ActivateProjectToolWindow`, `ActivateVersionControlToolWindow`); every other
Part 2 row has **no** Mac-specific override at all, so it silently inherits
`$default`'s Ctrl/Alt chord already — the README's old `⌘` labels for those
were simply wrong.

**Fourth pass (same day, real conflicts found in testing):** the first
attempt at the fix above assumed porting Windows' chord onto Mac was always
collision-free, since `$default` already owned that chord exclusively for
that action. That check only looked at whether the target *action id* had a
Mac override — it didn't check whether some *other* action already sat on
that same physical chord in the Mac-only files, the exact bug class the
F-row hot-set work already hit once. It had: `Mac OS X 10.5+.xml` secretly
gives `EditorLeft`/`EditorRight` (arrow-key caret movement) a *second*,
Emacs-style shortcut on `Ctrl+B`/`Ctrl+F`, invisible unless you diff every
action in the file, not just the ones you're touching. Claiming `Ctrl+B` for
`GotoDeclaration` and `Ctrl+F` for `Find` silently tied with those (plus
`TodoViewGroupByFlattenPackage`, also mac-only on `Ctrl+F`) — symptom: Find
and Go to Declaration didn't reliably fire. Fixed by re-declaring
`EditorLeft`/`EditorRight` with **only** their arrow-key shortcut (dropping
the Ctrl+B/F secondary; arrow-key navigation itself is unaffected) and fully
unbinding `TodoViewGroupByFlattenPackage`'s mac-only `Ctrl+F` assignment —
same empty-tag idiom as the F-row work. `Alt+1`/`Alt+9`/`Ctrl+Shift+F` had no
such hidden collision, verified clean. **Lesson:** "the target action has no
Mac override" is not the same question as "nothing else already owns this
chord on Mac" — always reverse-index every actual keystroke in the Mac-only
files against the new chord, not just look up the one action id you're
touching. `keymap-windows.xml` gets the same `EditorLeft`/`EditorRight`
entries redeclared for file symmetry (a no-op there — Windows never had a
Ctrl+B/F secondary to begin with).

**Fifth pass (2026-07-24, two-key simplification):** the `Ctrl+Alt+;`
leader (3-key first stroke) and the `Ctrl+Alt+<letter>` hot set (3-key
single chord) were retired after Roj reported finger strain and that the
leader was easy to misuse — see
`docs/superpowers/specs/2026-07-24-roj-keymap-two-key-simplification-design.md`
for the full design. Replaced with bare `Alt+<letter>` (2-key) for
high-frequency actions and a lighter `Alt+Minus` leader for the rest.
Applying the lesson from the fourth pass up front this time — every new
chord was reverse-indexed against the real bundled keymaps *before*
writing any XML, which caught real collisions beyond the ones anticipated
in the design doc (`Alt+Down` in particular contends with several
component-scoped actions: search-history dropdowns, list-navigation,
method-overload-switcher popups — all unbound for safety even though most
are scoped to specific UI components and may not have truly conflicted in
the editor). The old hot-set's inherited-conflict unbinds
(`Diff.ApplyLeftSide`, `UsageGrouping.DirectoryStructure`,
`ToggleRenderedDocPresentation`, `ToggleFindInSelection`,
`Console.History.Browse`) were removed since nothing of ours sits on
`Ctrl+Alt+<letter>` anymore except Back/Forward's arrows — those natives
get their original bindings back rather than staying pointlessly unbound.

## Uninstall

```sh
./install.py uninstall intellij
```

Removes the keymap file from every config dir. The IntelliJ app is left
installed (remove via `brew uninstall --cask intellij-idea-ce` or Finder). If
`roj-keymap` is still selected, switch back to a default keymap in Settings →
Keymap.
