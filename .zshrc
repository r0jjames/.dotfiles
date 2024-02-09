if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="powerlevel10k/powerlevel10k"
plugins=(
    git
    zsh-autosuggestions
    zsh-syntax-highlighting
    docker
)

source $ZSH/oh-my-zsh.sh

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# Alias here:
alias focus="timer 60m && terminal-notifier -message 'Pomodoro'\
        -title 'Work Timer is up! Take a Break 😊'\
        -appIcon '~/Pictures/pumpkin.jpeg'\
        -sound Crystal"
        
alias rest="timer 5m && terminal-notifier -message 'Pomodoro'\
        -title 'Break is over! Get back to work 😬'\
        -appIcon '~/Pictures/pumpkin.jpeg'\
        -sound Crystal"
# Shortcut to nvim
alias v='nvim'
# Shortcut to Kubectl
alias k='kubectl'
alias kubectl="minikube kubectl --"
# Make ls beautiful
alias ls='colorls'
# Press c to clear the terminal screen.
alias c='clear'
# Press h to view the bash history.
alias h='history'
# Display the directory structure better.
alias tree='tree --dirsfirst -F'
# Make a directory and all parent directories with verbosity.
alias mkdir='mkdir -p -v'
# Edit zshrc
alias edit="nvim ~/.zshrc"

# GIT 
# View Git status.
alias gs='git status'
# Add a file to Git.
alias ga='git add'
# Add all files to Git.
alias gaa='git add --all'

# Change Directories
# Move to the parent folder.
alias ..='cd ..;pwd'
# Move up two parent folders.
alias ...='cd ../..;pwd'
# Move up three parent folders.
alias ....='cd ../../..;pwd'

# View the calender by typing the first three letters of the month.
alias jan='cal -m 01'
alias feb='cal -m 02'
alias mar='cal -m 03'
alias apr='cal -m 04'
alias may='cal -m 05'
alias jun='cal -m 06'
alias jul='cal -m 07'
alias aug='cal -m 08'
alias sep='cal -m 09'
alias oct='cal -m 10'
alias nov='cal -m 11'
alias dec='cal -m 12'
lg()
{
    export LAZYGIT_NEW_DIR_FILE=~/.lazygit/newdir

    lazygit "$@"

    if [ -f $LAZYGIT_NEW_DIR_FILE ]; then
            cd "$(cat $LAZYGIT_NEW_DIR_FILE)"
            rm -f $LAZYGIT_NEW_DIR_FILE > /dev/null
    fi
}
# Generated for envman. Do not edit.
 [ -s "$HOME/.config/envman/load.sh" ] && source "$HOME/.config/envman/load.sh"

