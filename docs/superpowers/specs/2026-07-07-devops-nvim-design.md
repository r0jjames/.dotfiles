# DevOps Neovim Setup — Design

Date: 2026-07-07

## Goal

Turn the bare-bones, Terraform-only Neovim config into a DevOps writing/editing
environment for: Kubernetes, Helm, Docker, Python, Ansible, Terraform. Emphasis on
authoring `.yaml` (ansible / k8s / docker-compose) with on-save formatting plus
real-time linting so mistakes surface while learning.

## Decisions (from brainstorming)

- **Tool install:** Mason.nvim owns editor tooling (LSPs, formatters, linters).
  brew owns runnable CLIs.
- **Ansible detection:** standard directory layout → filetype `yaml.ansible`.
- **YAML formatter:** prettier (also formats JSON + Markdown).
- **Python:** ruff (format + lint), basedpyright (types).
- **Linters:** ansible-lint, hadolint, yamllint, tflint — all four.
- **Config layout:** split modular `lua/config` + `lua/plugins`.
- **CLIs to brew:** kubectl, helm, ansible, uv (+ keep terraform), hadolint.
- **Bonus:** treesitter (highlighting), bashls + lua_ls, stylua + shfmt.

## Config Layout

```
nvim/
  init.lua                 -- bootstrap lazy, require config modules, lazy.setup(import plugins)
  lua/
    config/
      options.lua          -- vim.opt
      keymaps.lua          -- leader maps (incl. neo-tree)
      lsp.lua              -- shared on_attach, capabilities, diagnostics UI
      filetypes.lua        -- ansible dir-layout detection -> yaml.ansible
    plugins/
      ui.lua               -- catppuccin, lualine, neo-tree, gitsigns
      treesitter.lua       -- nvim-treesitter (yaml, dockerfile, python, hcl, bash, lua, json, helm)
      mason.lua            -- mason + mason-lspconfig + mason-tool-installer
      lsp.lua              -- lspconfig server definitions
      completion.lua       -- nvim-cmp + luasnip + cmp-nvim-lsp
      formatting.lua       -- conform.nvim
      linting.lua          -- nvim-lint
```

`init.lua` keeps the lazy.nvim bootstrap, then
`require("lazy").setup({ import = "plugins" })` and requires the `config/*` modules.

## Plugins

Added:
- `mason-org/mason.nvim`
- `mason-org/mason-lspconfig.nvim`
- `WhoIsSethDaniel/mason-tool-installer.nvim`
- `nvim-treesitter/nvim-treesitter`
- `b0o/SchemaStore.nvim` (k8s / docker-compose / GitHub Actions JSON schemas for yaml-ls)
- `mfussenegger/nvim-lint`

Kept: catppuccin, neo-tree, lualine, gitsigns, nvim-lspconfig, nvim-cmp,
cmp-nvim-lsp, LuaSnip, conform.nvim. (hashivim/vim-terraform optional — treesitter
+ terraform_fmt cover it; keep for `:terraform` niceties.)

## LSP Servers (installed by Mason, enabled via nvim-lspconfig)

| Server                              | Handles                                   |
|-------------------------------------|-------------------------------------------|
| `yamlls`                            | k8s manifests, docker-compose (SchemaStore)|
| `ansiblels`                         | ansible playbooks / roles                 |
| `dockerls`                          | Dockerfile                                |
| `docker_compose_language_service`   | docker-compose.yml                        |
| `helm_ls`                           | Helm charts / templates                   |
| `basedpyright`                      | Python type checking / completion         |
| `ruff`                              | Python lint + format (LSP)                |
| `terraformls`                       | Terraform (kept)                          |
| `bashls`                            | shell scripts (bonus)                     |
| `lua_ls`                            | editing this nvim config (bonus)          |

### YAML routing (the crux)

`config/filetypes.lua` uses `vim.filetype.add` to map ansible-convention paths to
`yaml.ansible`:

- `**/playbooks/**/*.yml|yaml`
- `**/roles/**/tasks/*.yml|yaml`, `**/roles/**/handlers/*.yml|yaml`, `**/roles/**/meta/*.yml|yaml`
- `**/group_vars/**`, `**/host_vars/**`
- `**/inventories/**/*.yml|yaml`
- filename fallbacks: `playbook.yml`, `site.yml`, `*.ansible.yml|yaml`

Everything else stays filetype `yaml` → yaml-ls with SchemaStore (k8s + compose).
ansible-ls attaches only to `yaml.ansible`. yaml-ls is disabled on `yaml.ansible`
buffers to avoid double diagnostics.

## Formatters (conform.nvim, format_on_save)

| Filetype                    | Formatter        |
|-----------------------------|------------------|
| yaml, yaml.ansible, json, markdown | `prettier` |
| python                      | `ruff_format`    |
| terraform, tf               | `terraform_fmt`  |
| lua                         | `stylua`         |
| sh, bash                    | `shfmt`          |

`format_on_save` timeout 1000ms, `lsp_fallback = true`.

## Linters (nvim-lint, on BufWritePost + InsertLeave)

| Filetype      | Linter        |
|---------------|---------------|
| yaml          | `yamllint`    |
| yaml.ansible  | `ansible_lint`|
| dockerfile    | `hadolint`    |
| terraform     | `tflint`      |

yamllint tuned to relaxed (long lines / document-start off) to avoid noise while learning.

## setup-nvim.sh Changes

- Remove hand-rolled `terraform-ls` brew install and inline LSP config — Mason owns it.
- Keep: git check, neovim install, config-dir create, copy `nvim/` (init.lua + lua/),
  fontconfig, JetBrainsMono Nerd Font.
- brew-install CLIs (idempotent `command -v` guards): `kubectl`, `helm`, `ansible`,
  `uv`, `hadolint`, keep `terraform`.
- After `nvim --headless "+Lazy! sync" +qa`, run
  `nvim --headless "+MasonToolsInstall" +qa` so first boot installs all LSP/fmt/lint
  binaries unattended.
- Update final echo messages to reflect the DevOps stack.

## Out of Scope (YAGNI)

- Telescope / fuzzy finder (offer later if repo navigation needs it).
- DAP / debugging.
- which-key, autopairs, and other quality-of-life plugins.
- Go, Rust, or other languages not in the DevOps list.

## Success Criteria

- Open a k8s manifest → schema completion + validation, prettier on save.
- Open a file under `playbooks/` → treated as `yaml.ansible`, ansible-ls + ansible-lint.
- Open a Dockerfile → dockerls + hadolint diagnostics.
- Open a `.py` → basedpyright types, ruff lint, ruff format on save.
- `.tf` behaves as today (fmt + terraform-ls) but via Mason.
- Fresh machine: run `setup-nvim.sh` → everything installed unattended, `nvim` ready.
