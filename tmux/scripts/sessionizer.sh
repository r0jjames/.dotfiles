#!/usr/bin/env bash
# prefix+g — pick a project, land in a tmux session named after it.
#
# Runs inside `display-popup -E`, so stdin/stdout are a real tty and fzf
# works normally. One session per repo, reused on the next pick.
set -euo pipefail

ROOTS=("$HOME/Dev/projects" "$HOME/Dev" "$HOME/dev/projects" "$HOME/dev")

command -v fzf >/dev/null 2>&1 || {
  echo "fzf not installed — run ./install.py install zsh" >&2
  sleep 2
  exit 1
}

# Candidates are git repos at most two levels below a root. fd is much
# faster on large trees; find is the fallback so this works before the zsh
# module has installed anything.
# Device:inode identifies a directory regardless of how it was spelled.
# ~/Dev and ~/dev are the same directory on macOS's case-insensitive volume,
# and both spellings are in ROOTS, so name comparison would list every repo
# twice. This is also correct on case-sensitive Linux, where the two really
# are different directories and both survive.
dir_id() {
  stat -f '%d:%i' "$1" 2>/dev/null || stat -c '%d:%i' "$1" 2>/dev/null
}

list_projects() {
  local root id
  local -a seen=()
  for root in "${ROOTS[@]}"; do
    [ -d "$root" ] || continue
    id="$(dir_id "$root")"
    case " ${seen[*]-} " in *" $id "*) continue ;; esac
    seen+=("$id")
    if command -v fd >/dev/null 2>&1; then
      fd --hidden --no-ignore --max-depth 3 --type d '^\.git$' "$root" \
        --exec dirname
    else
      find "$root" -maxdepth 3 -type d -name .git -exec dirname {} \; \
        2>/dev/null
    fi
  done | sort -u
}

selected="$(list_projects | fzf --prompt='project> ' --height=100% \
  --border=none --no-multi)" || exit 0
[ -n "$selected" ] || exit 0

# tmux treats "." and ":" as session-name separators, so they cannot appear
# in one. ".dotfiles" would otherwise be unaddressable.
name="$(basename "$selected" | tr '.:' '__')"

tmux has-session -t "=$name" 2>/dev/null \
  || tmux new-session -d -s "$name" -c "$selected"

if [ -n "${TMUX:-}" ]; then
  tmux switch-client -t "=$name"
else
  tmux attach-session -t "=$name"
fi
