#!/usr/bin/env bash
# Neovim DevOps IDE: neovim + DevOps CLIs, config symlinked to ~/.config/nvim.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_os
ensure_brew

echo "🚀 Setting up Neovim for DevOps (k8s, Helm, Docker, Python, Ansible, Terraform)..."

brew_install git
brew_install neovim

# ---- DevOps CLIs (the tools you actually run; Mason handles editor tooling) ----
brew_install kubectl        # Kubernetes CLI
brew_install helm           # Helm charts
brew_install ansible        # Ansible + ansible-lint core
brew_install uv             # Python package/venv manager
brew_install hadolint       # Dockerfile linter (used by nvim + CLI)
brew_install terraform      # Terraform CLI (terraform_fmt formatter)

# ---- Fonts (icons in the UI) ----
if [ "$DOTFILES_OS" = "macos" ]; then
  brew_install fontconfig
  if fc-list | grep -qi "Nerd"; then
    ok "Nerd Font already installed."
  else
    brew_install font-jetbrains-mono-nerd-font --cask
  fi
else
  skip "Fonts render from the Windows-side terminal on WSL — install a Nerd Font on Windows (see README)."
fi

# ---- Config: symlink whole directory ----
link_file "$SCRIPT_DIR/config" "$HOME/.config/nvim"

# ---- Install plugins (headless) then Mason tools/servers ----
info "Syncing Neovim plugins (lazy.nvim)..."
nvim --headless "+Lazy! sync" +qa || true

info "Installing LSP servers, formatters, and linters (Mason)..."
# Waits for mason-tool-installer to finish, then quits. LSP servers listed in
# mason-lspconfig install concurrently; any stragglers finish on first launch.
nvim --headless -c "autocmd User MasonToolsUpdateCompleted quitall" -c "MasonToolsInstall" || true

echo "🎉 Neovim DevOps setup complete!"
echo "✅ LSP: yaml (k8s/compose), ansible, docker, helm, python, terraform, bash, lua"
echo "✅ Format on save: prettier (yaml/json/md), ruff (python), terraform_fmt"
echo "✅ Linting: yamllint, ansible-lint, hadolint, tflint"
echo "💡 Check tool status anytime with :Mason  and  :ConformInfo"
