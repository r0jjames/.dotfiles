#!/usr/bin/env bash
set -e

echo "🚀 Setting up Neovim..."

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
# Done
# ===============================
echo "🎉 Neovim setup complete! You can now run: nvim"
