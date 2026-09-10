# nvim

Neovim as a DevOps IDE: Kubernetes, Helm, Docker, Python, Ansible, Terraform.

## Run

```sh
./install.py install nvim
```

## What it installs

- **neovim** plus DevOps CLIs via Homebrew: `kubectl`, `helm`, `ansible`, `uv`, `hadolint`, `terraform`
- **Ubuntu:** neovim and `uv` from upstream into `~/.local`; `git`, `ansible` and
  `python3-venv` from apt. `python3-venv` is what lets Mason install its pip3-backed
  tools (basedpyright, yamllint, ansible-lint) — see the Platform notes.
- **JetBrainsMono Nerd Font** (macOS; on WSL install a Nerd Font on the Windows side instead)
- Symlinks [`config/`](config/) to `~/.config/nvim` — the whole config directory, so edits here are live
- Headless plugin sync (lazy.nvim) and Mason tool install (LSP servers, formatters, linters)

## Usage

Full keymap cheatsheet and workflow guide: [`config/README.md`](config/README.md) (also readable in-editor at `~/.config/nvim/README.md`).

- LSP: yaml (k8s/compose schemas), ansible, docker, helm, python, terraform, bash, lua
- Format on save: prettier (yaml/json/md), ruff (python), terraform_fmt
- Linting: yamllint, ansible-lint, hadolint, tflint
- Health checks: `:Mason`, `:ConformInfo`, `:checkhealth`

## Platform notes

- **WSL:** everything works in-terminal; icons need a Nerd Font set in Windows Terminal (see root README).
- **Ubuntu:** Mason installs basedpyright, yamllint and ansible-lint by building a
  venv per tool, so `python3-venv` must be present. Without it Neovim opens with
  `yamllint: failed to install` and `failed to install basedpyright` and nothing
  more; `:MasonLog` shows only `spawn: python3 failed with exit code 1`. Fix:

  ```sh
  sudo apt install -y python3-venv
  nvim --headless -c 'autocmd User MasonToolsUpdateCompleted quitall' -c MasonToolsInstall
  ```
