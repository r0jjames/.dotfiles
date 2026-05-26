#!/bin/bash

# How to use:
# Save the script as setup-terminal.sh
# Make it executable: chmod +x setup-terminal.sh
# Run it: ./setup-terminal.sh

# The script will:
# Install Homebrew if not already installed
# Install the Nerd Font and CLI tools via Homebrew
# Install Oh My Zsh
# Install Powerlevel10k theme
# Install zsh plugins (zsh-autosuggestions, zsh-syntax-highlighting)
# Backup the existing .zshrc
# Update .zshrc with the theme, plugins, aliases, and tool integrations
# Download and load all themes into Terminal.app
# Set MesloLGS NF as the default font
# Set Solarized Dark as the default theme
# # Install Homebrew if not already installed

if ! command -v brew &> /dev/null; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install font and CLI tools
brew install --cask font-meslo-lg-nerd-font
brew install bat eza fzf zoxide ripgrep fd htop

# Install Oh My Zsh
if [ ! -d ~/.oh-my-zsh ]; then
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

# Install Powerlevel10k theme
if [ ! -d ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k ]; then
  git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
fi

# Install zsh plugins
if [ ! -d ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions ]; then
  git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
fi
if [ ! -d ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting ]; then
  git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
fi

# Backup existing .zshrc
if [ -f ~/.zshrc ]; then
  cp ~/.zshrc ~/.zshrc.bak-$(date +%Y-%m-%d)
fi

# Update .zshrc
sed -i '' 's/^ZSH_THEME=.*/ZSH_THEME="powerlevel10k\/powerlevel10k"/' ~/.zshrc
sed -i '' 's/^plugins=.*/plugins=(\n  git\n  docker\n  docker-compose\n  kubectl\n  helm\n  terraform\n  ansible\n  aws\n  ssh-agent\n  zsh-autosuggestions\n  zsh-syntax-highlighting\n)/' ~/.zshrc

# Append aliases and tool integrations to .zshrc
cat >> ~/.zshrc << 'EOF'

# ---- DevOps aliases ----
alias k='kubectl'
alias kctx='kubectl config use-context'
alias kns='kubectl config set-context --current --namespace'
alias d='docker'
alias dc='docker compose'
alias tf='terraform'
alias ll='eza -lah --icons --git'
alias ls='eza --icons'
alias cat='bat --paging=never'
alias ..='cd ..'
alias ...='cd ../..'

# ---- Tool integrations ----
eval "$(fzf --zsh)"
eval "$(zoxide init zsh)"

# ---- fzf better defaults (use fd instead of find) ----
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
EOF

# Download and load Terminal themes
if [ ! -d ~/Downloads/macos-terminal-themes-master ]; then
  curl -L https://github.com/lysyi3m/macos-terminal-themes/archive/refs/heads/master.zip -o ~/Downloads/terminal-themes.zip
  unzip -o ~/Downloads/terminal-themes.zip -d ~/Downloads
  rm ~/Downloads/terminal-themes.zip
fi

osascript -e 'quit app "Terminal"'
sleep 2
for theme in ~/Downloads/macos-terminal-themes-master/themes/*.terminal; do
  open "$theme"
done
sleep 5
osascript -e 'quit app "Terminal"'

# Set MesloLGS NF as default font
defaults write com.apple.Terminal "Default Window Settings" -string "Solarized Dark"
defaults write com.apple.Terminal "Startup Window Settings" -string "Solarized Dark"
defaults write com.apple.Terminal "Font" -data-urlencode "MesloLGS NF Regular 13"

echo "Setup complete. Restart Terminal for all changes to take effect."