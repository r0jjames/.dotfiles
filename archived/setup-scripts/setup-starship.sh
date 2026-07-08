#!/usr/bin/env bash
set -e

echo "🚀 Setting up Starship..."

# ===============================
# Install Starship
# ===============================
if brew list starship &>/dev/null; then
  echo "✅ Starship already installed, skipping installation."
else
  echo "📦 Installing Starship..."
  brew install starship
fi

echo "🚀 Setting up Starship prompt..."
if command -v starship &> /dev/null; then
  if grep -Fxq 'eval "$(starship init zsh)"' ~/.zshrc; then
    echo "✅ Starship already initialized in ~/.zshrc, skipping..."
  else
    echo '⚡ Adding Starship initialization to ~/.zshrc...'
    echo 'eval "$(starship init zsh)"' >> ~/.zshrc
  fi
else
  echo "❌ Starship is not installed. Please install it first: https://starship.rs"
fi

# ===============================
# Copy starship.toml config
# ===============================
echo "📂 Copying starship.toml..."
mkdir -p ~/.config
cp ./starship/starship.toml ~/.config/starship.toml

# ===============================
# Zsh Syntax Highlighting
# ===============================
echo "🚀 Setting up Zsh syntax highlighting..."
if brew list zsh-syntax-highlighting &>/dev/null; then
  echo "✅ zsh-syntax-highlighting already installed."
else
  echo "📦 Installing zsh-syntax-highlighting..."
  brew install zsh-syntax-highlighting
fi

if grep -Fxq 'source $(brew --prefix)/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh' ~/.zshrc; then
  echo "✅ zsh-syntax-highlighting already in ~/.zshrc."
else
  echo '⚡ Adding zsh-syntax-highlighting to ~/.zshrc...'
  echo 'source $(brew --prefix)/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh' >> ~/.zshrc
fi

# ===============================
# Zsh Autosuggestions
# ===============================
echo "🚀 Setting up Zsh autosuggestions..."
if brew list zsh-autosuggestions &>/dev/null; then
  echo "✅ zsh-autosuggestions already installed."
else
  echo "📦 Installing zsh-autosuggestions..."
  brew install zsh-autosuggestions
fi

if grep -Fxq 'source $(brew --prefix)/share/zsh-autosuggestions/zsh-autosuggestions.zsh' ~/.zshrc; then
  echo "✅ zsh-autosuggestions already in ~/.zshrc."
else
  echo '⚡ Adding zsh-autosuggestions to ~/.zshrc...'
  echo 'source $(brew --prefix)/share/zsh-autosuggestions/zsh-autosuggestions.zsh' >> ~/.zshrc
fi

# ===============================
# Done
# ===============================
echo "🎉 Setup complete! Restart your terminal or run: source ~/.zshrc"
