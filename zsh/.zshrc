# Managed by the .dotfiles repo (symlinked here; clone path varies per machine
# — resolve with `readlink -f ~/.zshrc`). Machine-local tweaks, including
# DOTFILES_PROJECT_ROOTS for the tmux project picker, go in ~/.zshrc.local.

# ---- Homebrew (macOS Apple Silicon; also WSL, where brew is still used) ----
# A native Ubuntu desktop installs from apt instead and has no brew at all —
# both branches simply miss, which is the intent.
if [[ -x /home/linuxbrew/.linuxbrew/bin/brew ]]; then
  eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
elif [[ -x /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# ---- ~/.local/bin ----
# On Ubuntu this holds starship, lazygit and nvim (not in the archive, or too
# old there), plus the bat/fd shims. Ubuntu's ~/.profile adds it for login
# shells; add it here too so it is present regardless of how zsh was started.
[[ -d "$HOME/.local/bin" && ":$PATH:" != *":$HOME/.local/bin:"* ]] && \
  export PATH="$HOME/.local/bin:$PATH"

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
# These shadow core commands, so only alias them when the replacement is
# really there — on Ubuntu bat/fd are shimmed onto PATH from batcat/fdfind
# (see lib/apt.py), and a missing shim must not break plain `cat`.
command -v eza &>/dev/null && alias ll='eza -lah --icons --git'
command -v eza &>/dev/null && alias ls='eza --icons'
command -v bat &>/dev/null && alias cat='bat --paging=never'
alias ..='cd ..'
alias ...='cd ../..'
alias lg='lazygit'
alias vim='nvim'
alias vi='nvim'
alias v='nvim'
alias python="python3"
alias pip="pip3"
# The projects directory is spelled differently per machine (~/Dev on the
# Mac, ~/Development on the Ubuntu laptop), so resolve it instead of
# hardcoding one. Override by setting DEV_HOME in ~/.zshrc.local.
if [[ -z "$DEV_HOME" ]]; then
  for _d in "$HOME/Dev/projects" "$HOME/Dev" "$HOME/Development" "$HOME/dev"; do
    [[ -d "$_d" ]] && { DEV_HOME="$_d"; break; }
  done
  unset _d
fi
export DEV_HOME="${DEV_HOME:-$HOME}"
alias dev='cd "$DEV_HOME"'
alias projects='cd "$DEV_HOME"'
# .dotfiles sits next to the projects; follow ~/.zshrc back to the repo so
# this works no matter where the repo was cloned.
alias dot='cd "$(dirname "$(dirname "$(readlink -f "$HOME/.zshrc")")")"'

# ---- Tool integrations ----
# `fzf --zsh` only exists from fzf 0.48; Ubuntu 24.04 ships 0.44, where that
# call fails and would leave Ctrl-R/Ctrl-T unbound. Fall back to the shell
# files the Debian package installs.
if command -v fzf &>/dev/null; then
  if fzf --zsh &>/dev/null; then
    eval "$(fzf --zsh)"
  else
    for _f in /usr/share/doc/fzf/examples/key-bindings.zsh \
              /usr/share/doc/fzf/examples/completion.zsh \
              /usr/share/fzf/key-bindings.zsh \
              /usr/share/fzf/completion.zsh; do
      [[ -f "$_f" ]] && source "$_f"
    done
    unset _f
  fi
fi
command -v zoxide &>/dev/null && eval "$(zoxide init zsh)"

# ---- fzf better defaults (use fd instead of find) ----
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"

# ---- Zsh plugins (brew on macOS, apt on Ubuntu) ----
# Syntax highlighting must be sourced last of the two, so keep this order.
_plugin_dirs=()
command -v brew &>/dev/null && _plugin_dirs+=("$(brew --prefix)/share")
_plugin_dirs+=(/usr/share /usr/share/zsh/plugins)
for _sub in zsh-autosuggestions zsh-syntax-highlighting; do
  for _dir in "${_plugin_dirs[@]}"; do
    if [[ -f "$_dir/$_sub/$_sub.zsh" ]]; then
      source "$_dir/$_sub/$_sub.zsh"
      break
    fi
  done
done
unset _plugin_dirs _sub _dir

# ---- Prompt ----
command -v starship &>/dev/null && eval "$(starship init zsh)"

# ---- iTerm2 Shell Integration (macOS only; file exists only if installed) ----
test -e "${HOME}/.iterm2_shell_integration.zsh" && source "${HOME}/.iterm2_shell_integration.zsh"

# ---- Machine-local overrides (not managed by this repo) ----
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local

#THIS MUST BE AT THE END OF THE FILE FOR SDKMAN TO WORK!!!
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"

### MANAGED BY RANCHER DESKTOP START (DO NOT EDIT)
export PATH="/Users/roj/.rd/bin:$PATH"
### MANAGED BY RANCHER DESKTOP END (DO NOT EDIT)
export PATH="$HOME/.local/go/bin:$HOME/go/bin:$PATH"
