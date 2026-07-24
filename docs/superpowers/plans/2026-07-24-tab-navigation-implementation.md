# Tab Navigation (roj-keymap) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the dead `Alt+[`/`Alt+]` tab-cycle chords and document the two
already-native features (`Switcher`, numbered bookmarks) that satisfy
"find a file among open tabs" and "jump to a numbered slot."

**Architecture:** Two data-only XML edits (swap one chord pair in both
keymap files) plus a documentation update. No new code, no new test shapes —
the existing generic structural assertions in `tests/test_intellij.py`
already cover any chord data in these files.

**Tech Stack:** Plain XML (IntelliJ keymap scheme format), Python
`unittest` for verification, Markdown for docs.

## Global Constraints

- Mac and Windows keymap files must stay byte-identical (case-insensitive)
  in their relocated bindings — enforced by
  `test_mac_and_windows_bindings_are_identical`.
- No F1-F12 keys anywhere in a relocated chord.
- Every new chord must be reverse-indexed against the real bundled
  `$default.xml`/`Mac OS X.xml`/`Mac OS X 10.5+.xml` before writing —
  already done in the spec (`docs/superpowers/specs/2026-07-24-tab-navigation-design.md`):
  bare `Alt+H`/`Alt+L` have zero collisions in any of the three files.
- `keymap-macos.xml` uses lowercase letter tokens in `first-keystroke`
  (e.g. `alt r`); `keymap-windows.xml` uses uppercase (e.g. `alt R`). Match
  each file's existing casing convention when writing the new chords.
- Close IntelliJ before hand-editing a keymap XML file on a machine where
  it's running (it resaves the file on exit and would clobber the edit) —
  not relevant to this plan's execution (no IDE running), but keep in mind
  for the manual verification step.

---

### Task 1: Fix the dead tab-cycle chords

**Files:**
- Modify: `intellij/keymap-macos.xml:108-116`
- Modify: `intellij/keymap-windows.xml:73-78`
- Test: `tests/test_intellij.py` (existing, no changes needed — generic
  structural assertions apply to any chord data)

**Interfaces:** None — this is data-only XML, no functions/types involved.

- [ ] **Step 1: Confirm current state matches expectations**

Run: `grep -n -A2 'action id="NextEditorTab"\|action id="PreviousEditorTab"' intellij/keymap-macos.xml intellij/keymap-windows.xml`

Expected output:
```
intellij/keymap-macos.xml:108:  <action id="NextEditorTab">
intellij/keymap-macos.xml-109-    <keyboard-shortcut first-keystroke="alt close_bracket" />
intellij/keymap-macos.xml-110-  </action>
intellij/keymap-macos.xml:114:  <action id="PreviousEditorTab">
intellij/keymap-macos.xml-115-    <keyboard-shortcut first-keystroke="alt open_bracket" />
intellij/keymap-macos.xml-116-  </action>
intellij/keymap-windows.xml:73:  <action id="NextEditorTab">
intellij/keymap-windows.xml-74-    <keyboard-shortcut first-keystroke="alt CLOSE_BRACKET" />
intellij/keymap-windows.xml-75-  </action>
intellij/keymap-windows.xml:76:  <action id="PreviousEditorTab">
intellij/keymap-windows.xml-77-    <keyboard-shortcut first-keystroke="alt OPEN_BRACKET" />
intellij/keymap-windows.xml-78-  </action>
```

If line numbers or content differ, stop and re-read the file before editing
(something else changed it since this plan was written).

- [ ] **Step 2: Edit `intellij/keymap-macos.xml`**

Change:
```xml
  <action id="NextEditorTab">
    <keyboard-shortcut first-keystroke="alt close_bracket" />
  </action>
```
to:
```xml
  <action id="NextEditorTab">
    <keyboard-shortcut first-keystroke="alt l" />
  </action>
```

Change:
```xml
  <action id="PreviousEditorTab">
    <keyboard-shortcut first-keystroke="alt open_bracket" />
  </action>
```
to:
```xml
  <action id="PreviousEditorTab">
    <keyboard-shortcut first-keystroke="alt h" />
  </action>
```

- [ ] **Step 3: Edit `intellij/keymap-windows.xml`**

Change:
```xml
  <action id="NextEditorTab">
    <keyboard-shortcut first-keystroke="alt CLOSE_BRACKET" />
  </action>
```
to:
```xml
  <action id="NextEditorTab">
    <keyboard-shortcut first-keystroke="alt L" />
  </action>
```

Change:
```xml
  <action id="PreviousEditorTab">
    <keyboard-shortcut first-keystroke="alt OPEN_BRACKET" />
  </action>
```
to:
```xml
  <action id="PreviousEditorTab">
    <keyboard-shortcut first-keystroke="alt H" />
  </action>
```

- [ ] **Step 4: Run the test suite**

Run: `python -m unittest tests.test_intellij -v`
Expected: all tests pass (in particular
`test_mac_and_windows_bindings_are_identical`,
`test_no_duplicate_chord_within_a_file`,
`test_every_action_actually_has_a_chord`,
`test_no_function_key_survives_anywhere`).

- [ ] **Step 5: Commit**

```bash
git add intellij/keymap-macos.xml intellij/keymap-windows.xml
git commit -m "$(cat <<'EOF'
fix(intellij): replace dead Alt+[/] tab-cycle chords with Alt+H/L

Option+[ and Option+] are macOS input-method composition sequences
(produce curly quotes) and don't reliably reach IntelliJ's shortcut
dispatcher. Alt+H/Alt+L (vim left/right) avoid the punctuation-key
composition class entirely and are collision-free on both OS.
EOF
)"
```

---

### Task 2: Document Switcher, numbered bookmarks, and the chord fix

**Files:**
- Modify: `intellij/README.md` (Tier 1 table rows, new section, Verifying
  conflicts section)

**Interfaces:** None — documentation only.

- [ ] **Step 1: Update the Tier 1 table rows**

In `intellij/README.md`, find:
```markdown
| Extend Selection | `Alt+↑` |
| Shrink Selection | `Alt+↓` |
| New… (file/class/etc popup) | `Alt+N` |
| Select In (reveal current file) | `Alt+I` |
| Previous Editor Tab | `Alt+[` |
| Next Editor Tab | `Alt+]` |
| Back | `Ctrl+Alt+←` *(kept 3-key — see below)* |
| Forward | `Ctrl+Alt+→` *(kept 3-key — see below)* |
```
Replace with:
```markdown
| Extend Selection | `Alt+↑` |
| Shrink Selection | `Alt+↓` |
| New… (file/class/etc popup) | `Alt+N` |
| Select In (reveal current file) | `Alt+I` |
| Previous Editor Tab | `Alt+H` |
| Next Editor Tab | `Alt+L` |
| Back | `Ctrl+Alt+←` *(kept 3-key — see below)* |
| Forward | `Ctrl+Alt+→` *(kept 3-key — see below)* |
```

- [ ] **Step 2: Insert a new "Find & jump between tabs" section**

In `intellij/README.md`, find the end of the Tier 2 table and the start of
the next section:
```markdown
| Multi-cursor (next occurrence) | `Alt+-` `V` | | |

## Unchanged defaults (already identical, no override needed)
```
Replace with:
```markdown
| Multi-cursor (next occurrence) | `Alt+-` `V` | | |

## Find & jump between tabs (native, not overridden)

Neither of these needs a keymap edit — they're bundled IntelliJ defaults,
already identical on both OS, and roj-keymap doesn't touch them.

| Need | Chord | What it does |
|---|---|---|
| Find a file among open tabs | `Ctrl+Tab` (hold, tap `Tab` to cycle, release to jump) | Opens `Switcher`: a popup listing open editor tabs plus recent tool windows. `Ctrl+Shift+Tab` cycles it in reverse. |
| Jump straight to a pinned file | `Ctrl+1` .. `Ctrl+9` (`Ctrl+0` too) | `GotoBookmarkN`: jumps directly to whichever file/line you've assigned to slot N. |
| Pin a file to a numbered slot | `Ctrl+Shift+1` .. `Ctrl+Shift+9` | `ToggleBookmarkN`: assigns the current line/file to slot N (bookmarks are pinned by you — they don't track raw tab position, since IntelliJ has no "jump to tab position N" action at all). |

## Unchanged defaults (already identical, no override needed)
```

- [ ] **Step 3: Add a sixth "Verifying conflicts" pass entry**

In `intellij/README.md`, find the end of the fifth pass and the start of
the Uninstall section:
```markdown
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
```
Replace with:
```markdown
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

**Sixth pass (2026-07-24, tab navigation):** `Alt+[`/`Alt+]`
(Previous/Next Editor Tab) turned out unreliable on Mac — `Option+[` and
`Option+]` are macOS input-method composition sequences (they normally type
`"`/`'`), and punctuation keys held with Option can get consumed as
character composition before reaching IntelliJ's shortcut dispatcher, even
though the keymap itself is keycode-based and had no XML-level collision.
Replaced with `Alt+H`/`Alt+L` (vim left/right), which sit outside the
punctuation-key class and were confirmed collision-free against
`$default.xml`/`Mac OS X.xml`/`Mac OS X 10.5+.xml`. Separately, "find a
file among open tabs" and "jump to a numbered slot" turned out to already
have native answers (`Switcher` on `Ctrl+Tab`, `GotoBookmarkN` on
`Ctrl+1`-`9`) that roj-keymap had never touched — no XML change, just
added to the cheatsheet. Full rationale:
`docs/superpowers/specs/2026-07-24-tab-navigation-design.md`.

## Uninstall
```

- [ ] **Step 4: Commit**

```bash
git add intellij/README.md
git commit -m "$(cat <<'EOF'
docs(intellij): document Alt+H/L fix, Switcher, and bookmark jump

EOF
)"
```

---

## Self-Review Notes

- **Spec coverage:** Part 1 (cycle chord fix) → Task 1. Part 2 (Switcher)
  and Part 3 (bookmarks) → Task 2 Step 2. "Verifying conflicts" doc
  requirement from the spec → Task 2 Step 3. All three spec sections have
  a task.
- **Placeholder scan:** none found — every step shows exact before/after
  text or an exact command with expected output.
- **Type consistency:** N/A (no code, XML/Markdown only); action ids
  (`NextEditorTab`, `PreviousEditorTab`, `GotoBookmarkN`, `ToggleBookmarkN`,
  `Switcher`) are used consistently with the spec throughout.
