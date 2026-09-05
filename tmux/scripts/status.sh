#!/usr/bin/env bash
# Status-bar segments for tmux, one segment per invocation.
#
# These run on every status-interval tick (5s) for every attached client, so
# each branch must be cheap and must never block. Every branch exits 0 with
# no output when its tool or data is absent — the segment then collapses to
# nothing rather than showing an error or a stale value.
set -u

case "${1:-}" in
  k8s)
    command -v kubectl >/dev/null 2>&1 || exit 0
    # One kubectl call for both fields: --minify keeps current-context and
    # only the namespace of that context.
    read -r ctx ns <<<"$(kubectl config view --minify \
        -o 'jsonpath={.current-context} {..namespace}' 2>/dev/null)" || exit 0
    [ -n "${ctx:-}" ] || exit 0
    printf '⎈ %s' "$ctx"
    [ -n "${ns:-}" ] && printf '/%s' "$ns"
    ;;

  git)
    dir="${2:-}"
    [ -n "$dir" ] && [ -d "$dir" ] || exit 0
    command -v git >/dev/null 2>&1 || exit 0
    # Detached HEAD has no symbolic-ref; fall back to the short SHA.
    branch="$(git -C "$dir" symbolic-ref --quiet --short HEAD 2>/dev/null)" \
      || branch="$(git -C "$dir" rev-parse --short HEAD 2>/dev/null)" \
      || exit 0
    [ -n "$branch" ] || exit 0
    # --untracked-files=no keeps this fast in repos with large ignored trees.
    dirty=""
    [ -n "$(git -C "$dir" status --porcelain --untracked-files=no 2>/dev/null)" ] \
      && dirty="*"
    printf ' %s%s' "$branch" "$dirty"
    ;;
esac
