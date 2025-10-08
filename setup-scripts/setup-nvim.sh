#!/usr/bin/env bash
set -e

echo "🚀 Setting up Neovim..."

# ===============================
# Check for Git
# ===============================
if command -v git &>/dev/null; then
  echo "✅ Git already installed."
else
  echo "📦 Installing Git..."
  brew install git
fi

# ===============================
# Install Neovim
# ===============================
if brew list neovim &>/dev/null; then
  echo "✅ Neovim already installed, skipping installation."
else
  echo "📦 Installing Neovim..."
  brew install neovim
fi

# ===============================
# Create Neovim config folder
# ===============================
echo "📂 Creating Neovim config folder..."
mkdir -p ~/.config/nvim

# ===============================
# Copy init.lua (and lua/ folder if exists)
# ===============================
if [ -f ./nvim/init.lua ]; then
  echo "📂 Copying init.lua..."
  cp ./nvim/init.lua ~/.config/nvim/init.lua
fi

if [ -d ./nvim/lua ]; then
  echo "📂 Copying lua/ folder..."
  cp -r ./nvim/lua ~/.config/nvim/
fi

# ===============================
# Install Terraform CLI
# ===============================
if command -v terraform &>/dev/null; then
  echo "✅ Terraform CLI already installed, skipping installation."
else
  echo "📦 Installing Terraform CLI..."
  brew install terraform
fi

# ===============================
# Install Terraform Language Server (terraform-ls)
# ===============================
if command -v terraform-ls &>/dev/null; then
  echo "✅ terraform-ls already installed, skipping installation."
else
  echo "📦 Installing terraform-ls..."
  brew install hashicorp/tap/terraform-ls
fi

# ===============================
# Ensure fontconfig (for fc-list)
# ===============================
if command -v fc-list &>/dev/null; then
  echo "✅ fontconfig already installed."
else
  echo "📦 Installing fontconfig (for font detection)..."
  brew install fontconfig
fi

# ===============================
# Install Nerd Font (for icons)
# ===============================
if fc-list | grep -qi "Nerd" ; then
  echo "✅ Nerd Font already installed."
else
  echo "📦 Installing JetBrainsMono Nerd Font..."
  brew install --cask font-jetbrains-mono-nerd-font
fi

# ===============================
# Sync Lazy.nvim plugins (headless)
# ===============================
echo "⚙️  Syncing Neovim plugins..."
nvim --headless "+Lazy! sync" +qa || true

# ===============================
# Done
# ===============================
echo "🎉 Neovim setup complete!"
echo "✅ Terraform LSP and formatter configured."
echo "✨ You can now open Neovim with: nvim"

echo "🚀 Happy coding!"