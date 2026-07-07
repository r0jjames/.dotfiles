-- =============================
-- LSP server configuration (Neovim 0.11+ vim.lsp.config / vim.lsp.enable)
-- Mason installs the binaries (see plugins/mason.lua); this wires them up.
-- =============================
return {
  "neovim/nvim-lspconfig",
  dependencies = {
    "mason-org/mason-lspconfig.nvim",
    "hrsh7th/cmp-nvim-lsp",
    "b0o/schemastore.nvim",
  },
  event = { "BufReadPre", "BufNewFile" },
  config = function()
    local shared = require("config.lsp")
    shared.setup_diagnostics()

    local capabilities = shared.capabilities()
    local on_attach = shared.on_attach

    -- Defaults applied to every server
    vim.lsp.config("*", {
      capabilities = capabilities,
      on_attach = on_attach,
    })

    -- Per-server overrides
    local servers = {
      -- k8s manifests + docker-compose; schemas via SchemaStore
      yamlls = {
        settings = {
          yaml = {
            schemaStore = { enable = false, url = "" },
            schemas = require("schemastore").yaml.schemas(),
            validate = true,
            format = { enable = false }, -- prettier owns formatting
          },
        },
      },
      -- Ansible (attaches to yaml.ansible via lspconfig defaults)
      ansiblels = {},
      dockerls = {},
      docker_compose_language_service = {},
      helm_ls = {},
      -- Python: types from basedpyright, lint/format from ruff
      basedpyright = {
        settings = {
          basedpyright = {
            analysis = { typeCheckingMode = "basic" },
          },
        },
      },
      ruff = {},
      terraformls = {},
      bashls = {},
      lua_ls = {
        settings = {
          Lua = {
            diagnostics = { globals = { "vim" } }, -- silence nvim global warnings
            workspace = { checkThirdParty = false },
            telemetry = { enable = false },
          },
        },
      },
    }

    for name, cfg in pairs(servers) do
      vim.lsp.config(name, cfg)
      vim.lsp.enable(name)
    end
  end,
}
