# Global conventions

- Claude Code config is managed in the dotfiles repo's `claude/` directory —
  `settings.json`, `statusline-command.sh`, and this file land in `~/.claude/`.
  The repo's clone path differs per machine (`~/Dev/.dotfiles` on the Mac,
  `~/Development/.dotfiles` on the Ubuntu laptop); resolve it with
  `dirname "$(readlink -f ~/.claude/CLAUDE.md)"` rather than assuming either.
  Change config through the repo and commit; never edit the `~/.claude` copies
  in place.
  On macOS/Linux they are symlinks (same files). On Windows/Git Bash they are
  copies — re-run `./install.py install claude` after editing.
- Heavy stack plugins (`vercel`, `supabase`, `frontend-design`) are disabled
  globally to keep sessions lean. Enable per project via that repo's
  `.claude/settings.json` `enabledPlugins` (see `worship-lineup` for the pattern).
- The `MCP_DOCKER` MCP server only connects when Rancher Desktop is
  running; a failed connection there is expected, not a config bug.
- Walkthrough skills (`roj-explain-logic`, `roj-investigate-issue`, `roj-soundboarding`,
  `roj-code-review-pr`) **do not write a CodeTour by default** — a tour is a whole
  extra generation pass, and most walkthroughs are read once and never
  replayed. Finish the walkthrough, then offer the tour in one line and wait
  for a yes before chaining to `code-tour`. Build it from evidence already
  gathered, never a second investigation pass. "make a tour" in the original
  request skips the confirmation. `.tours/` is in the global git ignore
  (`git/ignore`), so tours stay local.
- Asking for a tour outright (`code-tour`, `roj-tour-codebase`, "tour this repo")
  is the request itself — build it, no confirmation.
- Onboarding into an unfamiliar repo goes through `roj-tour-codebase`, which owns
  those triggers: it runs `acquire-codebase-knowledge` for discovery, then
  writes a chained tour series into `.tours/`. Use
  `acquire-codebase-knowledge` on its own only when docs are wanted without
  tours. Its `docs/codebase/` output is not covered by the global git ignore
  — offer `.git/info/exclude`, never edit a repo's `.gitignore`.
- Commits to ANY repository use Roj's git identity ONLY. Never add Claude as an
  author, co-author, or trailer (no `Co-Authored-By`, no `Claude-Session`, no
  "Generated with Claude" footers) in commit messages or PR bodies.
- `graphify` (knowledge-graph CLI, installed by `agent-skills/install.py` as an
  external skill) stays **skill-only**: invoke it as `/graphify .`, never as an
  always-on block. This bullet is also the guard — `graphify install` appends
  its own always-on section to `~/.claude/CLAUDE.md` (a symlink to this file)
  unless the word graphify already appears here. Keep the word.
