#!/bin/bash

# Install Homebrew if not already installed
if ! command -v brew &> /dev/null; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install iTerm2 if not already installed
if [ ! -d "/Applications/iTerm.app" ]; then
  brew install --cask iterm2
fi

# Install font and CLI tools if not already installed
if ! brew list --cask | grep -q "font-meslo-lg-nerd-font"; then
  brew install --cask font-meslo-lg-nerd-font
fi
for tool in bat eza fzf zoxide ripgrep fd htop; do
  if ! command -v $tool &> /dev/null; then
    brew install $tool
  fi
done

# Shell stack (oh-my-zsh, p10k, plugins, .zshrc) is owned by setup-zsh.sh
"$(dirname "$0")/setup-zsh.sh"

# Install iTerm2 Shell Integration if not already installed
# (the .zshrc template already sources this file, no need to append)
if [ ! -f ~/.iterm2_shell_integration.zsh ]; then
  curl -fsSL https://iterm2.com/shell_integration/zsh -o ~/.iterm2_shell_integration.zsh
fi

# Install iTerm2 dynamic profile (color theme + font) if not already installed
mkdir -p ~/Library/Application\ Support/iTerm2/DynamicProfiles
cp ./iterm2/com.dotfiles.json ~/Library/Application\ Support/iTerm2/DynamicProfiles/com.dotfiles.json

# Set the dotfiles profile as the default for new windows/tabs
defaults write com.googlecode.iterm2 "Default Bookmark Guid" -string "557036D3-EF41-4D30-A395-3F301A17D49B"

echo "Setup complete. Restart iTerm2 (Cmd+Q then relaunch) for the theme and default profile to take effect."
