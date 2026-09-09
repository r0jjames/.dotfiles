#!/bin/sh
input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // empty')
model=$(echo "$input" | jq -r '.model.display_name // empty')
remaining=$(echo "$input" | jq -r '.context_window.remaining_percentage // empty')

# Shorten cwd to tilde-prefixed form. settings.json runs this with `sh`,
# which is bash on macOS but dash on Ubuntu -- so no ${var/#pat/sub}, which
# is a bashism and aborts the line with "Bad substitution" under dash.
home="$HOME"
case "$cwd" in
  "$home")   short_cwd="~" ;;
  "$home"/*) short_cwd="~${cwd#"$home"}" ;;
  *)         short_cwd="$cwd" ;;
esac

# Get git branch (skip optional locks to avoid interference)
branch=$(git -C "$cwd" branch --show-current 2>/dev/null)

# Build status line
line="$short_cwd"
[ -n "$branch" ] && line="$line ($branch)"
[ -n "$model" ] && line="$line | $model"
[ -n "$remaining" ] && line="$line | $(printf '%.0f' "$remaining")% left"

echo "$line"
