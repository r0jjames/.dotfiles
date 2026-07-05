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

# Install Oh My Zsh if not already installed
if [ ! -d ~/.oh-my-zsh ]; then
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

# Install Powerlevel10k theme if not already installed
if [ ! -d ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k ]; then
  git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
fi

# Install zsh plugins if not already installed
if [ ! -d ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions ]; then
  git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
fi
if [ ! -d ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting ]; then
  git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
fi

# Backup existing .zshrc if it exists and hasn't been backed up today
if [ -f ~/.zshrc ] && [ ! -f ~/.zshrc.bak-$(date +%Y-%m-%d) ]; then
  cp ~/.zshrc ~/.zshrc.bak-$(date +%Y-%m-%d)
fi

# Update .zshrc theme if not already set
if ! grep -q "ZSH_THEME=\"powerlevel10k/powerlevel10k\"" ~/.zshrc; then
  sed -i '' 's/^ZSH_THEME=.*/ZSH_THEME="powerlevel10k\/powerlevel10k"/' ~/.zshrc
fi

# Update .zshrc plugins if not already set
if ! grep -q "plugins=(\n  git\n  docker" ~/.zshrc; then
  sed -i '' 's/^plugins=.*/plugins=(\n  git\n  docker\n  docker-compose\n  kubectl\n  helm\n  terraform\n  ansible\n  aws\n  ssh-agent\n  zsh-autosuggestions\n  zsh-syntax-highlighting\n)/' ~/.zshrc
fi

# Append aliases and tool integrations to .zshrc if not already present
if ! grep -q "# ---- DevOps aliases ----" ~/.zshrc; then
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
fi

# Install iTerm2 Shell Integration if not already installed
if [ ! -f ~/.iterm2_shell_integration.zsh ]; then
  curl -fsSL https://iterm2.com/shell_integration/zsh -o ~/.iterm2_shell_integration.zsh
fi
if ! grep -q "iterm2_shell_integration.zsh" ~/.zshrc; then
  cat >> ~/.zshrc << 'EOF'

# ---- iTerm2 Shell Integration ----
test -e "${HOME}/.iterm2_shell_integration.zsh" && source "${HOME}/.iterm2_shell_integration.zsh"
EOF
fi

# Install iTerm2 dynamic profile (color theme + font) if not already installed
mkdir -p ~/Library/Application\ Support/iTerm2/DynamicProfiles
cp ./iterm2/com.dotfiles.json ~/Library/Application\ Support/iTerm2/DynamicProfiles/com.dotfiles.json

# Set the dotfiles profile as the default for new windows/tabs
defaults write com.googlecode.iterm2 "Default Bookmark Guid" -string "557036D3-EF41-4D30-A395-3F301A17D49B"

echo "Setup complete. Restart iTerm2 (Cmd+Q then relaunch) for the theme and default profile to take effect."
