# Global conventions

- Claude Code config is managed in `~/Dev/.dotfiles/claude/` — `settings.json`,
  `statusline-command.sh`, and this file are symlinked into `~/.claude/`.
  Change config through the repo and commit; never edit the `~/.claude` copies
  in place (they are the same files).
- Heavy stack plugins (`vercel`, `supabase`, `frontend-design`) are disabled
  globally to keep sessions lean. Enable per project via that repo's
  `.claude/settings.json` `enabledPlugins` (see `worship-lineup` for the pattern).
- The `MCP_DOCKER` MCP server only connects when Docker Desktop is running;
  a failed connection there is expected, not a config bug.
