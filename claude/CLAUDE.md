# Global conventions

- Claude Code config is managed in `~/Dev/.dotfiles/claude/` — `settings.json`,
  `statusline-command.sh`, and this file land in `~/.claude/`. Change config
  through the repo and commit; never edit the `~/.claude` copies in place.
  On macOS/Linux they are symlinks (same files). On Windows/Git Bash they are
  copies — re-run `./install.py install claude` after editing.
- Heavy stack plugins (`vercel`, `supabase`, `frontend-design`) are disabled
  globally to keep sessions lean. Enable per project via that repo's
  `.claude/settings.json` `enabledPlugins` (see `worship-lineup` for the pattern).
- The `MCP_DOCKER` MCP server only connects when Rancher Desktop is
  running; a failed connection there is expected, not a config bug.
- Walkthrough skills (`explain-logic`, `investigate-issue`, `soundboarding`,
  `code-review-pr`) end by writing a CodeTour file into `.tours/`
  in the repo being worked on — chain to the `code-tour` skill, built from
  evidence already gathered, no second investigation pass. Skip it only when
  all of: one file, no cross-file flow, under ~3 steps — then say so in one
  line with the reason. "make a tour" overrides a skip, "no tour" overrides
  the default. `.tours/` is in the global git ignore (`git/ignore`), so tours
  stay local.
- Onboarding into an unfamiliar repo goes through `tour-codebase`, which owns
  those triggers: it runs `acquire-codebase-knowledge` for discovery, then
  writes a chained tour series into `.tours/`. Use
  `acquire-codebase-knowledge` on its own only when docs are wanted without
  tours. Its `docs/codebase/` output is not covered by the global git ignore
  — offer `.git/info/exclude`, never edit a repo's `.gitignore`.
- Commits to ANY repository use Roj's git identity ONLY. Never add Claude as an
  author, co-author, or trailer (no `Co-Authored-By`, no `Claude-Session`, no
  "Generated with Claude" footers) in commit messages or PR bodies.
