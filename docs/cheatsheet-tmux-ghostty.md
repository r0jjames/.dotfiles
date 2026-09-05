# Terminal cheat sheet — Ghostty + tmux

Two layers of keys sit on top of each other. Knowing which layer owns a key
is most of the battle:

- **Ghostty** owns anything with **⌘ (Super)**. It never reaches the shell.
- **tmux** owns anything after **`Ctrl-b`** (the prefix), plus a few `Alt`
  keys. It never reaches Ghostty.
- Everything else goes to the program in the pane.

Generated against **Ghostty 1.3.1** and **tmux 3.7c**, the versions this repo
installs. Regenerate the raw lists any time:

```sh
ghostty +list-keybinds --default        # or the app binary under /Applications
tmux list-keys -T prefix
tmux list-keys -T copy-mode
```

Keys marked **★** are added by this repo ([`tmux/tmux.conf`](../tmux/tmux.conf)).
Everything unmarked is stock — this repo rebinds nothing.

---

## Which layer should I use?

Ghostty and tmux both do tabs and splits, and they do not know about each
other. Pick one and stay there:

| Want | Use | Why |
|---|---|---|
| Splits and tabs inside one terminal window | **tmux** | Survives closing the window, reattaches after a reboot, works identically over SSH |
| A second terminal window | **Ghostty** (`⌘N`) | tmux has no concept of an OS window |
| Search scrollback | **Ghostty** (`⌘F`) for the live screen, **tmux copy mode** (`prefix [`) for tmux's 50k-line buffer | Different buffers |

The short version: use tmux for everything inside the window, Ghostty for the
window itself.

---

## tmux

Prefix is **`Ctrl-b`**. Press it, release, then press the key.
`prefix ?` lists every binding live.

### Sessions

| Key | Does |
|---|---|
| `prefix d` | detach (the session keeps running) |
| `prefix s` | session tree, switch between sessions |
| `prefix $` | rename session |
| `prefix (` / `prefix )` | previous / next session |
| `prefix L` | last session |
| **★** `prefix g` | fzf project picker — one session per repo |

From outside tmux:

```sh
tmux                      # new unnamed session
tmux new -s work          # new named session
tmux ls                   # list sessions
tmux attach -t work       # attach
tmux kill-session -t work
```

### Windows (tabs)

| Key | Does |
|---|---|
| `prefix c` | new window |
| `prefix 0`–`prefix 9` | go to window by number (**0-indexed**, as tmux ships) |
| `prefix n` / `prefix p` | next / previous window |
| `prefix l` | last window |
| `prefix w` | window tree, pick visually |
| `prefix ,` | rename window |
| `prefix &` | kill window (asks first) |
| `prefix .` | move window to another index |
| `prefix f` | find window by name |
| `Alt-n` / `Alt-p` | next / previous window **with activity** |

### Panes (splits)

| Key | Does |
|---|---|
| `prefix %` | split left/right |
| `prefix "` | split top/bottom |
| `prefix x` | kill pane (asks first) |
| `prefix z` | zoom pane to full window, again to restore |
| `prefix o` | cycle to next pane |
| `prefix ;` | last pane |
| `prefix q` | show pane numbers; press one to jump |
| `prefix {` / `prefix }` | swap pane with previous / next |
| `prefix Space` | cycle through layouts |
| `prefix Alt-1`…`Alt-7` | pick a layout directly (even-h, even-v, main-h, main-v, tiled, …) |
| `prefix E` | spread panes out evenly |
| `prefix !` | break pane out into its own window |
| `prefix arrows` | move focus |
| **★** `prefix Ctrl-h/j/k/l` | move focus, vim-style |
| `prefix Ctrl-arrows` | resize by 1 |
| `prefix Alt-arrows` | resize by 5 |
| **★** `prefix Alt-h/j/k/l` | resize by 5, vim-style (hold to repeat) |

> `l` and `L` are deliberately **not** pane keys here — tmux ships them as
> last-window and last-session. That is why the vim letters live behind
> `Ctrl` and `Alt`.

### Copy mode / scrollback

`prefix [` enters copy mode; `q` or `Escape` leaves. Keys are **emacs-style**,
which is the tmux default and is left alone by this repo. The mouse works too:
drag to select, and the selection is copied on release.

| Key | Does |
|---|---|
| `prefix [` | enter copy mode |
| `prefix PageUp` | enter copy mode and scroll up one page |
| `Ctrl-Space` | start selection |
| `Alt-w` or `Ctrl-w` | copy selection and exit |
| `R` | toggle rectangle (block) selection |
| `prefix ]` | paste the tmux buffer |
| `prefix =` | choose from older buffers |
| `Ctrl-s` / `Ctrl-r` | incremental search down / up |
| `n` / `N` | next / previous match |
| `g` | go to line number |
| `Alt-<` / `Alt->` | top / bottom of history |
| `Ctrl-v` / `Alt-v` | page down / page up |
| `Alt-Down` / `Alt-Up` | half page down / up |
| `Ctrl-a` / `Ctrl-e` | start / end of line |
| `Alt-b` / `Alt-f` | previous word / end of next word |
| `f` / `F` | jump forward / backward to a character |

Copies land in the macOS clipboard (`set-clipboard on` via OSC 52), so `⌘V`
works in any app afterwards.

### Housekeeping

| Key | Does |
|---|---|
| `prefix ?` | list every binding |
| `prefix :` | tmux command prompt |
| `prefix t` | big clock |
| `prefix r` | redraw the client |
| **★** `prefix R` | reload `tmux.conf` |
| `prefix ~` | show recent tmux messages |
| `prefix C` | interactive options editor |

### Reading the status bar

```
▐  dotfiles ▓ 0 nvim ▒ 1 •zsh ▒ 2 claude      ◤ ⎈ prod/api ◀  main* ◀ 14:32 ▌
```

- Left segment **amber** = prefix is live, the next key goes to tmux.
- Left segment **purple** = normal.
- `` after a window name = that window has a zoomed pane.
- `*` after the branch = working tree is dirty (tracked files only).
- Kube and git segments disappear entirely when `kubectl`/`git` are absent.

---

## Ghostty

`⌘` is Super. These never reach tmux or the shell.

### Windows, tabs, splits

| Key | Does |
|---|---|
| `⌘N` | new window |
| `⌘T` | new tab |
| `⌘1`–`⌘8` | go to tab 1–8 |
| `⌘9` | last tab |
| `⌘⇧[` / `⌘⇧]` | previous / next tab |
| `Ctrl-Tab` / `Ctrl-⇧-Tab` | next / previous tab |
| `⌘D` | split right |
| `⌘⇧D` | split down |
| `⌘[` / `⌘]` | previous / next split |
| `⌘⌥arrows` | move focus between splits |
| `⌘Ctrl-arrows` | resize split by 10 |
| `⌘Ctrl-=` | equalize splits |
| `⌘⇧Enter` | zoom the split |
| `⌘Enter` | fullscreen |
| `⌘Ctrl-F` | fullscreen (non-native) |
| `⌘W` | close split/tab (the current surface) |
| `⌘⌥W` | close tab |
| `⌘⇧W` | close window |

### Copy, paste, search

| Key | Does |
|---|---|
| `⌘C` / `⌘V` | copy / paste |
| `⌘⇧V` | paste from the selection buffer |
| `⌘A` | select all |
| `⇧arrows` | extend the selection |
| `⌘F` | search |
| `⌘G` / `⌘⇧G` | next / previous match |
| `⌘E` | search for the current selection |
| `Escape` or `⌘⇧F` | end search |

### Scrolling and prompts

| Key | Does |
|---|---|
| `⌘Home` / `⌘End` | top / bottom of scrollback |
| `⌘PageUp` / `⌘PageDown` | page up / down |
| `⌘arrow-up` / `⌘arrow-down` | jump to previous / next shell prompt |
| `⌘⇧arrow-up` / `⌘⇧arrow-down` | same, by prompt |
| `⌘J` | scroll to the selection |
| `⌘K` | clear screen |

### Appearance and config

| Key | Does |
|---|---|
| `⌘+` / `⌘-` | font size up / down |
| `⌘0` | reset font size |
| `⌘,` | open config ([`ghostty/config`](../ghostty/config)) |
| `⌘⇧,` | reload config |
| `⌘⇧P` | command palette |
| `⌘⌥I` | terminal inspector |
| `⌘Q` | quit |

### Line editing that Ghostty sends to the shell

These are not terminal actions — Ghostty translates them into control codes
your shell already understands:

| Key | Sends | Effect in zsh |
|---|---|---|
| `⌘arrow-left` | `Ctrl-a` | jump to start of line |
| `⌘arrow-right` | `Ctrl-e` | jump to end of line |
| `⌘Backspace` | `Ctrl-u` | delete to start of line |
| `⌥arrow-left` | `Esc b` | back one word |
| `⌥arrow-right` | `Esc f` | forward one word |

`⌥` reaches the shell (and tmux's `Alt-` keys) because this repo sets
`macos-option-as-alt = true`. Without it macOS would swallow Option for
accented characters.

---

## Overlaps worth knowing

| Key | Ghostty takes it | So in tmux, use |
|---|---|---|
| `⌘K` | clear screen | `Ctrl-l` in the shell |
| `⌘F` | Ghostty search (live screen only) | `prefix [` then `Ctrl-s` for tmux's full history |
| `⌘1`–`⌘9` | Ghostty tabs | `prefix 0`–`prefix 9` for tmux windows |
| `⌘D` | Ghostty split | `prefix %` / `prefix "` for tmux panes |

`Ctrl-b` is only tmux's if you are inside tmux. Outside it, `Ctrl-b` is the
shell's "back one character" as usual.

---

## Related

- [`tmux/README.md`](../tmux/README.md) — what the config does and why
- [`ghostty/README.md`](../ghostty/README.md) — theme and font
- [`zsh/README.md`](../zsh/README.md) — aliases and fzf keybindings
