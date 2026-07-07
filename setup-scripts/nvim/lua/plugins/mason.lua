-- =============================
-- Mason: installs LSP servers, formatters, and linters into Neovim's data dir
-- =============================
return {
  {
    "mason-org/mason.nvim",
    build = ":MasonUpdate",
    opts = {
      ui = { border = "rounded" },
    },
  },

  -- Installs the LSP servers listed here. Actual server config is in plugins/lsp.lua.
  {
    "mason-org/mason-lspconfig.nvim",
    dependencies = { "mason-org/mason.nvim" },
    opts = {
      ensure_installed = {
        "yamlls",
        "ansiblels",
        "dockerls",
        "docker_compose_language_service",
        "helm_ls",
        "basedpyright",
        "ruff",
        "terraformls",
        "bashls",
        "lua_ls",
      },
      -- Servers are enabled from plugins/lsp.lua via vim.lsp.enable,
      -- so mason-lspconfig should not auto-enable them a second time.
      automatic_enable = false,
    },
  },

  -- Installs the non-LSP tools (formatters + linters) by Mason package name.
  {
    "WhoIsSethDaniel/mason-tool-installer.nvim",
    dependencies = { "mason-org/mason.nvim" },
    opts = {
      ensure_installed = {
        "prettier",
        "stylua",
        "shfmt",
        "yamllint",
        "ansible-lint",
        "hadolint",
        "tflint",
      },
      run_on_start = true,
    },
  },
}
