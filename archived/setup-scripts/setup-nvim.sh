#!/usr/bin/env bash
set -e

echo "🚀 Setting up Neovim for DevOps (k8s, Helm, Docker, Python, Ansible, Terraform)..."

# ===============================
# Helpers
# ===============================
# brew_install <formula> [--cask] : install only if missing
brew_install() {
  local pkg="$1"
  shift || true
  if brew list "$pkg" &>/dev/null; then
    echo "✅ $pkg already installed."
  else
    echo "📦 Installing $pkg..."
    brew install "$@" "$pkg"
  fi
}

# ===============================
# Prerequisites
# ===============================
if ! command -v brew &>/dev/null; then
  echo "❌ Homebrew not found. Install it first: https://brew.sh"
  exit 1
fi

if command -v git &>/dev/null; then
  echo "✅ Git already installed."
else
  echo "📦 Installing Git..."
  brew install git
fi

# ===============================
# Install Neovim
# ===============================
brew_install neovim

# ===============================
# DevOps CLIs (the tools you actually run; Mason handles editor tooling)
# ===============================
brew_install kubectl        # Kubernetes CLI
brew_install helm           # Helm charts
brew_install ansible        # Ansible + ansible-lint core
brew_install uv             # Python package/venv manager
brew_install hadolint       # Dockerfile linter (used by nvim + CLI)
brew_install terraform      # Terraform CLI (terraform_fmt formatter)

# ===============================
# Fonts (icons in the UI)
# ===============================
if command -v fc-list &>/dev/null; then
  echo "✅ fontconfig already installed."
else
  echo "📦 Installing fontconfig (for font detection)..."
  brew install fontconfig
fi

if fc-list | grep -qi "Nerd"; then
  echo "✅ Nerd Font already installed."
else
  echo "📦 Installing JetBrainsMono Nerd Font..."
  brew install --cask font-jetbrains-mono-nerd-font
fi

# ===============================
# Copy Neovim config (init.lua + modular lua/ tree)
# ===============================
echo "📂 Syncing Neovim config to ~/.config/nvim..."
mkdir -p ~/.config/nvim

if [ -f ./nvim/init.lua ]; then
  cp ./nvim/init.lua ~/.config/nvim/init.lua
fi

if [ -f ./nvim/README.md ]; then
  # Usage cheatsheet, so `:e ~/.config/nvim/README.md` works in-editor.
  cp ./nvim/README.md ~/.config/nvim/README.md
fi

if [ -d ./nvim/lua ]; then
  # Refresh the lua/ tree so removed modules don't linger.
  rm -rf ~/.config/nvim/lua
  cp -r ./nvim/lua ~/.config/nvim/
fi

# ===============================
# Install plugins (headless) then Mason tools/servers
# ===============================
echo "⚙️  Syncing Neovim plugins (lazy.nvim)..."
nvim --headless "+Lazy! sync" +qa || true

echo "⚙️  Installing LSP servers, formatters, and linters (Mason)..."
# Waits for mason-tool-installer to finish, then quits. LSP servers listed in
# mason-lspconfig install concurrently; any stragglers finish on first launch.
nvim --headless -c "autocmd User MasonToolsUpdateCompleted quitall" -c "MasonToolsInstall" || true

# ===============================
# Done
# ===============================
echo "🎉 Neovim DevOps setup complete!"
echo "✅ LSP: yaml (k8s/compose), ansible, docker, helm, python, terraform, bash, lua"
echo "✅ Format on save: prettier (yaml/json/md), ruff (python), terraform_fmt"
echo "✅ Linting: yamllint, ansible-lint, hadolint, tflint"
echo "💡 Ansible files auto-detected under playbooks/ roles/ group_vars/ host_vars/ inventories/"
echo "🔎 Check tool status anytime with :Mason  and  :ConformInfo"
echo "✨ Open Neovim with: nvim"
echo "🚀 Happy coding!"
