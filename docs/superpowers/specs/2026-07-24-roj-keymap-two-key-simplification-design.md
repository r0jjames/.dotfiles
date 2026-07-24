# roj-keymap: two-key simplification

## Problem

The `Ctrl+Alt+;`-leader design (from the earlier unification work,
`2026-07-24-roj-keymap-unification-design.md`) works but is heavy: every
non-hot-set action requires a 3-key first stroke (`Ctrl+Alt+;`) followed by
a second stroke, and even the "hot set" itself is a 3-key chord
(`Ctrl+Alt+<letter>`). Roj reports this hurts his fingers and is hard to
remember, cutting into the productivity the redesign was supposed to buy.
Testing also surfaced that pressing multi-stroke chords by *holding* the
first chord's modifiers into the second stroke (natural muscle memory) does
not fire the action — IntelliJ matches the second stroke's modifiers
literally, so `Ctrl+Alt+;` must be fully released before the second key.

## Goal

Rebuild the custom chord space so that:

1. High-frequency actions use a **bare 2-key chord** (`Alt+<letter>` or
   `Alt+<arrow>`), never a leader.
2. Nothing exceeds **3 keys**, and multi-stroke chords are minimized to the
   genuine long tail.
3. The leader itself (for whatever doesn't fit in the 2-key tier) shrinks
   from a 3-key first stroke (`Ctrl+Alt+;`) to a 2-key one (`Alt+Minus`).
4. Mac and Windows stay byte-identical, per the existing test
   (`test_mac_and_windows_bindings_are_identical`).
5. Every new chord is verified against the real bundled
   `Mac OS X.xml`/`Mac OS X 10.5+.xml`/`$default.xml` (extracted from
   `app-client.jar`) *before* being written — not after Roj hits a
   collision on real hardware, which happened twice during the prior phase.

## Why `Alt+<letter>` solves the scarcity problem

The prior design's `Ctrl+Alt+<letter>` hot set was nearly full (bundled
defaults already claim ~9 of 26 letters there for real refactor actions).
Reverse-indexing bare `Alt+<letter>` against the same bundled files shows
it is almost entirely **unclaimed** on both OS — only 4 letters (`J`, `M`,
`O`, `Q`) collide, all with minor/rare actions
(`SelectNextOccurrence`-alias, `Vcs.ToggleAmendCommitMode`,
`ExportToTextFile`, `EditorContextInfo`). This is what makes a flat 2-key
tier viable where it wasn't before.

`Alt+Minus` (the new leader prefix) is confirmed completely free as a
first-keystroke on both OS — no bundled action anywhere uses it, so — like
the old semicolon leader — it is structurally collision-free by
construction; only the individual bare 2-key promotions need per-chord
verification.

## Chord map

### Tier 0 — Ctrl-based (unchanged from Part 3, plus one addition)

| Action | Chord | Note |
|---|---|---|
| Go to Declaration | `Ctrl+B` | existing |
| Find | `Ctrl+F` | existing |
| Find in Path | `Ctrl+Shift+F` | existing |
| Project tool window | `Alt+1` | existing |
| VCS tool window | `Alt+9` | existing |
| **Close tab** (`CloseContent`) | **`Ctrl+W`** | **new** — see below |

### Tier 1 — bare `Alt+<key>` (2-key, high frequency)

| Action | Chord | Was |
|---|---|---|
| Rename | `Alt+R` | Ctrl+Alt+R |
| Find Usages | `Alt+U` | Ctrl+Alt+U |
| Toggle Breakpoint | `Alt+K` | Ctrl+Alt+K |
| Step Over | `Alt+D` | Ctrl+Alt+D |
| Step Into | `Alt+G` | Ctrl+Alt+G |
| Step Out | `Alt+Q` | Ctrl+Alt+Q |
| Evaluate Expression | `Alt+E` | Ctrl+Alt+E |
| Run | `Alt+W` | Ctrl+Alt+W |
| Debug | `Alt+X` | Ctrl+Alt+X |
| Go to Class | `Alt+C` | leader `;` Shift+C |
| Go to File | `Alt+F` | leader `;` F |
| Go to Symbol | `Alt+S` | leader `;` Y |
| Terminal | `Alt+T` | leader `;` T |
| Build (CompileDirty) | `Alt+B` | leader `;` K |
| Extend Selection | `Alt+↑` | leader `;` Up |
| Shrink Selection | `Alt+↓` | leader `;` Down |
| New… (file/class/etc popup) | `Alt+N` | *(new)* |
| Select In (reveal current file) | `Alt+I` | leader `;` I |
| Previous Editor Tab | `Alt+[` | *(new)* |
| Next Editor Tab | `Alt+]` | *(new)* |

**Exception — Back/Forward stay 3-key:** `Alt+Left`/`Alt+Right` collide with
`PreviousTab`/`NextTab` (Windows, heavily used) *and* `EditorPreviousWord`/
`EditorNextWord` (Mac — Option+Arrow word-navigation, a fundamental
system-wide macOS text-editing convention). Forcing these to 2-key would be
a worse regression than the chords they'd replace. Back/Forward remain at
`Ctrl+Alt+←`/`Ctrl+Alt+→`, unchanged from Part 1.

Direct jump-to-tab-N (`Cmd+1`..`Cmd+9`, the browser convention Roj asked
about) does not exist as an IntelliJ action — verified against the full
bundled action set, only `NextEditorTab`/`PreviousEditorTab` (cycle one at
a time) exist. `Alt+[`/`Alt+]` above is the closest available substitute.

### Tier 2 — leader (`Alt+Minus` then a key)

Everything else currently in the old `Ctrl+Alt+;`-leader set moves here
**unchanged in its second keystroke** — only the first-keystroke prefix
changes, from `Ctrl+Alt+Semicolon` to `Alt+Minus`:

ChangeSignature (`C`), ChooseDebugConfiguration (`Shift+X`),
ChooseRunConfiguration (`Shift+W`), EditSourceInNewWindow (`O`),
EditorDeleteLine (`Backspace`), FileStructurePopup (`S`), Generate (`G`,
demoted from Tier 1 to make room for `Alt+N`/New…), GotoNextError (`E`),
GotoPreviousError (`Shift+E`), HideAllWindows (`J`), JumpToLastWindow
(`W`), Move (`M`), NextDiff (`N`), PreviousDiff (`Shift+N`), QuickJavaDoc
(`D`), Refactorings.QuickListPopupAction (`Q`), Resume (`R`), RunToCursor
(`U`), ShowBookmarks (`Shift+B`), ShowErrorDescription (`Shift+D`),
ShowExecutionPoint (`P`), SmartStepInto (`A`), Stop (`X`), ToggleBookmark
(`B`), SelectNextOccurrence (`V`).

## New collisions requiring unbinds

Verified by reverse-indexing every new Tier 0/1 chord against the real
bundled `$default.xml`/`Mac OS X.xml`/`Mac OS X 10.5+.xml` (same method as
the Part 3/4 fixes). To be re-confirmed at implementation time immediately
before editing, per the recurring lesson of this project:

| Chord | Colliding action | OS | Disposition |
|---|---|---|---|
| `Ctrl+W` | `UsageFiltering.WriteAccess` (rare Find-Usages filter) | both | unbind |
| `Alt+Q` | `EditorContextInfo` (rare, duplicate of `Ctrl+Shift+Q`) | windows only | unbind |
| `Alt+↑` | `MethodUp` (jump to previous method) | windows only | unbind — Mac already natively binds `Alt+↑` to `EditorSelectWord`, no mac-side change needed |
| `Alt+↓` | `MethodDown` (jump to next method); `ShowSearchHistory`/`List-selectLastRow` (component-scoped, low risk) | windows (+ scoped mac entries) | unbind `MethodDown`; scoped ones checked at implementation time since they only fire with a specific component focused |

`Ctrl+W` was chosen over the native-per-OS alternative (`Cmd+W` mac /
`Ctrl+W` win) to stay consistent with this project's core rule: identical
chords on both OS, not an OS-native convention. This overrides Mac's native
`Cmd+W`→`CloseContent` binding (dropped as a side effect of redeclaring
`CloseContent`'s shortcut list to `Ctrl+W` only, same mechanism as every
prior override in this project).

## Docs

`intellij/README.md`'s cheatsheet is restructured around the three tiers
above, replacing the current "Hot set / Leader set" framing. The
"Verifying conflicts" section gains a fifth pass documenting this rewrite,
consistent with the existing running history of passes 1-4.

## Tests

`tests/test_intellij.py`'s structural assertions (well-formed XML, no
F-keys, every action has a chord, Mac/Windows identical, no duplicate
chord, unbind hygiene, keymap name) apply unchanged — just more/different
data through the same shapes. `KNOWN_CONFLICTS` gains the 3-4 new entries
from the table above (mirroring the existing `(chord, action_id, os)`
tuple format).

## Verification

Same as prior phases: `python -m unittest tests.test_intellij` after
editing, plus Roj testing on real hardware (Mac now, Citrix VDI once
`keymap-windows.xml` syncs). Given this phase already caused two rounds of
"doesn't work" surprises from under-verified collisions, implementation
must re-run the reverse-index check for every chord in this doc
immediately before writing the XML, not rely solely on this doc's
snapshot.
