# How to use:
# Save the script as setup-terminal.sh
# Make it executable: chmod +x setup-terminal.sh
# Run it: ./setup-terminal.sh

# The script will:
# Install Homebrew if not already installed
# Install the Nerd Font and CLI tools via Homebrew
# Run setup-zsh.sh (oh-my-zsh, powerlevel10k, zsh plugins, .zshrc)
# Download and load all themes into Terminal.app
# Set MesloLGS NF as the default font
# Set Solarized Dark as the default theme

#!/bin/bash

# Install Homebrew if not already installed
if ! command -v brew &> /dev/null; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
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

# Download and load Terminal themes if not already downloaded
if [ ! -d ~/Downloads/macos-terminal-themes-master ]; then
  curl -L https://github.com/lysyi3m/macos-terminal-themes/archive/refs/heads/master.zip -o ~/Downloads/terminal-themes.zip
  unzip -o ~/Downloads/terminal-themes.zip -d ~/Downloads
  rm ~/Downloads/terminal-themes.zip
fi

# Load themes into Terminal if not already loaded
osascript -e 'quit app "Terminal"'
sleep 2
for theme in ~/Downloads/macos-terminal-themes-master/themes/*.terminal; do
  theme_name=$(basename "$theme" .terminal)
  if ! defaults read com.apple.Terminal "Window Settings" | grep -q "$theme_name"; then
    open "$theme"
  fi
done
sleep 5
osascript -e 'quit app "Terminal"'

# Set MesloLGS NF as default font if not already set
if ! defaults read com.apple.Terminal "Font" | grep -q "MesloLGS NF"; then
  defaults write com.apple.Terminal "Default Window Settings" -string "Solarized Dark"
  defaults write com.apple.Terminal "Startup Window Settings" -string "Solarized Dark"
  defaults write com.apple.Terminal "Font" -data-urlencode "MesloLGS NF Regular 13"
fi

echo "Setup complete. Restart Terminal for all changes to take effect."