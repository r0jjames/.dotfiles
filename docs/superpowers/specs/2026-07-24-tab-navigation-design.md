# roj-keymap: tab navigation (cycle fix + find + jump)

## Problem

Roj wants to more easily navigate editor tabs in IntelliJ when many files are
open: jump to a specific tab (first, second, etc.), and quickly find a file
among the open tabs. Separately, the existing cycle chords
`Alt+[`/`Alt+]` (`PreviousEditorTab`/`NextEditorTab`, added in the two-key
simplification pass) are reported not working on Mac.

## Root cause of the broken cycle chords

`Alt+[` and `Alt+]` have no collision in the keymap XML itself (verified:
no other action in `keymap-macos.xml` claims `alt open_bracket`/
`alt close_bracket`, and the parent chain — `Mac OS X 10.5+.xml` — has no
plain-`alt`-modified bracket binding either, only `meta`/`meta alt`
variants). The likely cause is a known macOS/JetBrains-runtime issue: on the
US keyboard layout, `Option+[` and `Option+]` are input-method composition
sequences that produce `"`/`'` characters. Punctuation keys held with Option
can get consumed as character composition before they reach the shortcut
dispatcher, even though IntelliJ's keymap is keycode-based. Digit and letter
chords (`Alt+1`, `Alt+R`, etc.) don't hit this because plain letters/digits
don't compose. Roj hadn't isolated the exact symptom (quote character typed
vs. nothing at all) at spec time — the fix below sidesteps the whole
punctuation-key class regardless of the precise mechanism, so no further
isolation is needed before implementing.

## Goal

1. Replace the cycle chords with keys outside the punctuation-composition
   risk class, so they work reliably on both OS.
2. Give Roj a way to find a file among many open tabs.
3. Give Roj a way to jump directly to a specific tab-like slot by number,
   understanding IntelliJ has no raw "tab position N" action (re-confirmed
   against the real bundled action set — only cycle actions exist).

## Design

### 1. Cycle chords: `Alt+H` / `Alt+L`

Replace `PreviousEditorTab`/`NextEditorTab`'s chords:

| Action | Old | New |
|---|---|---|
| Previous Editor Tab | `Alt+[` | `Alt+H` |
| Next Editor Tab | `Alt+]` | `Alt+L` |

Vim-style left/right mnemonic. Verified zero collision for bare `Alt+H` /
`Alt+L` against the real bundled `$default.xml`, `Mac OS X.xml`, and
`Mac OS X 10.5+.xml` (no first-keystroke match at all — cleaner than the
brackets were), and against roj-keymap's own Tier 1/Tier 2 letter
assignments (`H`/`L` unused in both).

### 2. Find a file among open tabs: `Switcher` (native, no edit)

IntelliJ's built-in `Switcher` action (hold `Ctrl+Tab`, tap `Tab` repeatedly
to move through the list, release to jump; `Ctrl+Shift+Tab` reverses) lists
open editor tabs plus recently used tool windows. It is not currently bound
by roj-keymap, so it inherits `Ctrl+Tab`/`Ctrl+Shift+Tab` from the parent
chain unchanged — and that inherited binding is already byte-identical on
both OS in the bundled defaults. No XML change needed; this is a
documentation-only addition to the cheatsheet. Roj verifies the exact
list/filter behavior in the running IDE, since it can't be exercised
headlessly.

### 3. Jump to a numbered slot: `Ctrl+1`-`Ctrl+9` bookmarks (native, no edit)

No IntelliJ action jumps to "tab position N" — only cycle actions exist in
the full bundled action set. The closest real substitute is numbered
bookmarks, which IntelliJ already binds identically on both OS and which
roj-keymap does not currently override:

| Action | Chord | Effect |
|---|---|---|
| `ToggleBookmarkN` (N = 0-9) | `Ctrl+Shift+<N>` | Assign bookmark slot N to the current line/file |
| `GotoBookmarkN` (N = 0-9) | `Ctrl+<N>` | Jump straight to slot N from anywhere |

This gives direct 1-key jump to up to 10 pinned files — not raw tab
position (bookmarks don't shift when tabs open/close/reorder, unlike a
literal "tab 2"), which Roj accepted as the trade-off versus the two-key
simplification design's earlier finding that no positional-jump action
exists. No XML change needed; documentation-only.

## Non-goals

- No attempt to fake positional tab-N jumping (e.g. via a plugin or script)
  — out of scope, native-action-only per this project's established
  approach.
- Not touching any other Tier 0/1/2 chord.

## Docs

`intellij/README.md`:
- Tier 1 table: update Previous/Next Editor Tab rows to `Alt+H`/`Alt+L`.
- New cheatsheet subsection (under "Unchanged defaults" or its own small
  section) documenting `Switcher` (`Ctrl+Tab`/`Ctrl+Shift+Tab`) and the
  bookmark slots (`Ctrl+1..9` / `Ctrl+Shift+1..9`), each noting "native,
  not overridden by roj-keymap."
- "Verifying conflicts" section gains a sixth pass entry: the `Alt+[`/`]`
  Mac composition-bug finding and the `Alt+H`/`Alt+L` replacement.

## Tests

`tests/test_intellij.py`'s existing structural assertions apply unchanged —
`Alt+H`/`Alt+L` replace `Alt+[`/`Alt+]` as plain data in both
`keymap-macos.xml`/`keymap-windows.xml`, same shape. No new `KNOWN_CONFLICTS`
entries needed since both new chords are collision-free. No test changes
needed for Switcher/bookmarks since nothing in the XML changes for them.

## Verification

`python -m unittest tests.test_intellij` after editing. Manual in-IDE check
on Mac: `Alt+H`/`Alt+L` cycle tabs, `Ctrl+Tab` opens Switcher, `Ctrl+Shift+1`
then `Ctrl+1` round-trips a bookmark jump. Windows/VDI check deferred to
whenever Roj is next on that machine, consistent with how prior phases
handled cross-machine verification.
