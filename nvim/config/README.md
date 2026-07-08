# Neovim DevOps Setup — Usage Guide

A practical cheatsheet for this Neovim config. Written for macOS. Keep it open in a
split (`:vsplit ~/.config/nvim/README.md`) while the muscle memory forms.

- Leader key = **Spacebar**. "`<leader>e`" means **Space then e**.
- `C-` = **Control**. `S-` = **Shift**. `M-` = **Option/Alt** (see macOS notes).
- Most keys below only work in **Normal mode** (press `Esc` first if unsure).

---

## 1. First launch

```bash
cd ~/Dev/.dotfiles/setup-scripts && ./setup-nvim.sh   # one-time install
nvim                                                   # open editor
```

Then inside Neovim:

| Command         | What it shows                                         |
|-----------------|-------------------------------------------------------|
| `:Mason`        | LSP servers / formatters / linters install status     |
| `:Lazy`         | Plugin manager (sync, update, profile)                |
| `:ConformInfo`  | Which formatters run for the current file             |
| `:checkhealth`  | Diagnose anything broken (LSP, treesitter, providers) |
| `:LspInfo`      | Language servers attached to the current buffer       |

If a tool shows as not installed in `:Mason`, press `i` on its line to install it.

---

## 2. Modes (the core idea)

Neovim is modal — the same key does different things per mode.

| Mode        | Enter it with        | Purpose                          |
|-------------|----------------------|----------------------------------|
| **Normal**  | `Esc`                | Move, run commands (default)     |
| **Insert**  | `i` `a` `o`          | Type text                        |
| **Visual**  | `v` (`V` line, `C-v` block) | Select text                |
| **Command** | `:`                  | Run `:commands`                  |

`i` insert before cursor · `a` after · `o` new line below · `O` new line above.
Always return to Normal with `Esc`. Save & quit lives in Command mode below.

---

## 3. Survival commands (Command mode, start with `:`)

| Command      | Action                          |
|--------------|---------------------------------|
| `:w`         | Save                            |
| `:q`         | Quit                            |
| `:wq` / `:x` | Save and quit                   |
| `:q!`        | Quit, discard changes           |
| `:wa`        | Save all buffers                |
| `:e <file>`  | Open a file                     |
| `:vsplit`    | Split window vertically         |
| `:split`     | Split window horizontally       |

Move between splits: `C-w` then `h` `j` `k` `l` (left/down/up/right).

---

## 4. Moving around (Normal mode)

| Key            | Move                                   |
|----------------|----------------------------------------|
| `h` `j` `k` `l`| left / down / up / right               |
| `w` / `b`      | next / previous word                   |
| `0` / `$`      | start / end of line                    |
| `gg` / `G`     | top / bottom of file                   |
| `{` / `}`      | previous / next paragraph (block)      |
| `C-u` / `C-d`  | half page up / down                    |
| `%`            | jump to matching bracket               |
| `/text` `Enter`| search forward (`n` next, `N` prev)    |
| `:42`          | jump to line 42                        |

## 5. Editing (Normal mode)

| Key        | Action                                  |
|------------|-----------------------------------------|
| `x`        | delete character                        |
| `dd`       | delete (cut) line                       |
| `yy`       | yank (copy) line                        |
| `p` / `P`  | paste after / before                    |
| `u`        | undo                                    |
| `C-r`      | redo                                    |
| `cw`       | change word                             |
| `.`        | repeat last change                      |
| `>>` / `<<`| indent / outdent line                   |
| `gcc`      | (if commented plugin present) — else use `I# `/visual block |

Combine verb + motion: `d}` delete to next paragraph, `y$` yank to end of line,
`ciw` change inner word. This grammar is the whole point of Vim.

---

## 6. Custom keymaps (this config)

**General**

| Key          | Action                        |
|--------------|-------------------------------|
| `<leader>e`  | Toggle file explorer (Neo-tree)|
| `<leader>d`  | Show diagnostics for the line |
| `[d` / `]d`  | Previous / next diagnostic    |
| `Esc`        | Clear search highlight        |

**Code intelligence (LSP — active when a language server attaches)**

| Key          | Action                                    |
|--------------|-------------------------------------------|
| `gd`         | Go to definition                          |
| `gr`         | Find references                           |
| `K`          | Hover docs (types, description)           |
| `<leader>rn` | Rename symbol (project-wide)              |
| `<leader>ca` | Code action (quick fixes, refactors)      |

**Autocompletion (Insert mode, while the popup is visible)**

| Key         | Action                          |
|-------------|---------------------------------|
| `C-Space`   | Trigger completion              |
| `Tab` / `S-Tab` | Next / previous suggestion  |
| `Enter`     | Accept selected suggestion      |
| `C-f` / `C-b` | Scroll docs popup down / up   |
| `C-e`       | Dismiss completion              |

---

## 7. File explorer (Neo-tree)

Open with `<leader>e`. Inside the tree (Normal mode):

| Key       | Action                     |
|-----------|----------------------------|
| `Enter`   | Open file / expand folder  |
| `a`       | Add file (end with `/` for a folder) |
| `d`       | Delete                     |
| `r`       | Rename                     |
| `c` / `m` | Copy / move                |
| `H`       | Toggle hidden files        |
| `?`       | Show all Neo-tree keys     |
| `q`       | Close the tree             |

---

## 8. Formatting & linting

- **Format runs automatically on save** (conform.nvim). Just `:w`.
- Formatters by filetype: `prettier` (yaml/json/markdown), `ruff` (python),
  `terraform_fmt`, `stylua` (lua), `shfmt` (shell).
- **Linters run on save / leaving insert** (nvim-lint): `yamllint`, `ansible-lint`,
  `hadolint`, `tflint`. Problems appear as inline diagnostics.
- Jump between problems with `]d` / `[d`; read the full message with `<leader>d`.
- `:ConformInfo` — see/troubleshoot which formatter ran.

---

## 9. DevOps workflow by file type

**Kubernetes / docker-compose (`.yaml`)** — plain YAML files use
`yaml-language-server` with schemas. You get key completion and validation against
the k8s / compose schema. `K` on a field shows its docs.

**Ansible** — files under `playbooks/`, `roles/*/tasks|handlers|meta/`,
`group_vars/`, `host_vars/`, `inventories/`, or named `playbook.yml` / `site.yml` /
`*.ansible.yml` are auto-detected as `yaml.ansible`. They get the Ansible language
server + `ansible-lint`. Check the active filetype with `:set filetype?` — should
print `yaml.ansible`. To force it on any file: `:set filetype=yaml.ansible`.

**Dockerfile** — `dockerls` completion + `hadolint` best-practice warnings.

**Helm** — chart templates under `templates/` are treated as `helm` so Go-template
syntax doesn't break YAML parsing; `helm-ls` provides intelligence.

**Python** — `basedpyright` for types/completion, `ruff` for linting, `ruff` format
on save. Use `uv` in the terminal for envs: `uv venv && uv pip install ...`.

**Terraform** — `terraform-ls` + `terraform_fmt` on save + `tflint`.

---

## 10. Managing the setup

| Command                | Purpose                                   |
|------------------------|-------------------------------------------|
| `:Lazy sync`           | Install/update/clean plugins              |
| `:Lazy update`         | Update plugins only                       |
| `:Mason`               | Manage LSP/formatter/linter binaries      |
| `:MasonToolsUpdate`    | Update the auto-installed tools           |
| `:TSUpdate`            | Update treesitter parsers                 |
| `:TSInstall <lang>`    | Add a parser (e.g. `:TSInstall go`)       |
| `:checkhealth`         | Full diagnostic report                    |

Re-running `./setup-nvim.sh` re-syncs config, plugins, and tools from the repo.

---

## 11. macOS notes

- **Clipboard is shared with the system** (`clipboard = unnamedplus`). `y` copies to
  the macOS clipboard and `p` pastes from it — so `Cmd-C` in a browser then `p` in
  Neovim works, and `y` here then `Cmd-V` elsewhere works too.
- **`Cmd` is a terminal key, not a Neovim key.** Neovim can't see `Cmd-S` etc.; use
  the Vim commands (`:w`, `dd`, `yy`). That's expected, not a bug.
- **Option key / `M-` mappings:** for Meta/Alt shortcuts to work, your terminal must
  send them. In iTerm2: *Preferences → Profiles → Keys → Left Option key = Esc+*.
  In WezTerm it works by default. This config doesn't rely on `M-` keys, so you can
  skip this unless you add your own.
- **Mouse works** (`mouse = a`) — click to move, drag to select — but learning the
  keyboard motions is faster long-term.
- If icons look like boxes, your terminal font must be the **JetBrainsMono Nerd
  Font** (installed by the setup script); select it in your terminal profile.

---

## 12. Where things live

```
~/.config/nvim/                 (synced from this repo's nvim/ folder)
  init.lua                       bootstrap, leader key, loads the modules below
  lua/config/
    options.lua                  editor settings (numbers, indent, clipboard)
    keymaps.lua                  the general keymaps in section 6
    filetypes.lua                Ansible/Helm detection + per-language indent
    lsp.lua                      shared LSP keymaps (gd/gr/K/...) + diagnostics UI
  lua/plugins/
    ui.lua                       colorscheme, statusline, file tree, git signs
    treesitter.lua               syntax highlighting
    mason.lua                    installs LSPs / formatters / linters
    lsp.lua                      language server configuration
    completion.lua               autocompletion + snippets
    formatting.lua               format-on-save rules
    linting.lua                  linter rules
```

To change a keymap, edit `lua/config/keymaps.lua` (or `lua/config/lsp.lua` for the
LSP ones), save, and restart Neovim. To add a plugin, drop a new file in
`lua/plugins/` returning a lazy spec — it's picked up automatically.

---

## Learn faster

- Run `:Tutor` inside Neovim — the built-in 30-minute interactive tutorial.
- `:help <topic>` for anything (e.g. `:help vim.lsp.buf.rename`).
- Press `?` inside Neo-tree, `:Mason`, or `:Lazy` to see their local keymaps.
