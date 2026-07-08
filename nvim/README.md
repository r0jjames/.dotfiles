# nvim

Neovim as a DevOps IDE: Kubernetes, Helm, Docker, Python, Ansible, Terraform.

## Run

```sh
./nvim/setup.sh        # or: ./install.sh nvim
```

## What it installs

- **neovim** plus DevOps CLIs via Homebrew: `kubectl`, `helm`, `ansible`, `uv`, `hadolint`, `terraform`
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
