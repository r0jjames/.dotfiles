#!/usr/bin/env bash
set -e

echo "🚀 Setting up WezTerm..."

# Check if wezterm is already installed
if brew list --cask wezterm &>/dev/null; then
  echo "✅ WezTerm already installed, skipping installation."
else
  echo "📦 Installing WezTerm..."
  brew install --cask wezterm
fi

# font
if brew install --cask font-go-mono-nerd-font &>/dev/null; then
  echo "✅ Go mono nerd font installed"
else
  echo "📦 Installing mono nerd font...."
  brew install --cask font-go-mono-nerd-font
fi

# Create wezterm config directory
echo "📂 Creating WezTerm config folder..."
mkdir -p ~/.config/wezterm

# Copy local wezterm config files
echo "📂 Copying wezterm configurations..."
cp ./wezterm/wezterm.lua ~/.config/wezterm/wezterm.lua
cp ./wezterm/events.lua ~/.config/wezterm/events.lua
# cp ./wezterm/config.lua ~/.config/wezterm/config.lua

# Restart WezTerm if running
if pgrep -x "WezTerm" > /dev/null; then
  echo "🔄 Restarting WezTerm..."
  pkill WezTerm
  sleep 2
  open -a WezTerm
else
  echo "✅ WezTerm is not running, launching..."
  open -a WezTerm
fi

echo "🎉 Setup complete!"
