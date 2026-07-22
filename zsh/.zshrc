# Managed by ~/Dev/.dotfiles (symlinked). Machine-local tweaks go in ~/.zshrc.local.

# ---- Homebrew (Linux/WSL needs this on PATH; macOS Apple Silicon too) ----
if [[ -x /home/linuxbrew/.linuxbrew/bin/brew ]]; then
  eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
elif [[ -x /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# ---- Completion ----
autoload -Uz compinit && compinit

# ---- History ----
HISTFILE=~/.zsh_history
HISTSIZE=50000
SAVEHIST=50000
setopt SHARE_HISTORY HIST_IGNORE_DUPS HIST_IGNORE_SPACE

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
alias vim='nvim'
alias vi='nvim'
alias v='nvim'
alias python="python3"
alias pip="pip3"

# ---- Tool integrations ----
command -v fzf &>/dev/null && eval "$(fzf --zsh)"
command -v zoxide &>/dev/null && eval "$(zoxide init zsh)"

# ---- fzf better defaults (use fd instead of find) ----
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"

# ---- Zsh plugins (installed via brew) ----
if command -v brew &>/dev/null; then
  _brew_prefix="$(brew --prefix)"
  [[ -f "$_brew_prefix/share/zsh-autosuggestions/zsh-autosuggestions.zsh" ]] && \
    source "$_brew_prefix/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
  [[ -f "$_brew_prefix/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ]] && \
    source "$_brew_prefix/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
  unset _brew_prefix
fi

# ---- Prompt ----
command -v starship &>/dev/null && eval "$(starship init zsh)"

# ---- iTerm2 Shell Integration (macOS only; file exists only if installed) ----
test -e "${HOME}/.iterm2_shell_integration.zsh" && source "${HOME}/.iterm2_shell_integration.zsh"

# ---- Machine-local overrides (not managed by this repo) ----
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local

#THIS MUST BE AT THE END OF THE FILE FOR SDKMAN TO WORK!!!
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"
