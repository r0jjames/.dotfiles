-- =============================
-- Formatting: conform.nvim (format on save)
-- =============================
return {
  "stevearc/conform.nvim",
  event = { "BufWritePre" },
  cmd = { "ConformInfo" },
  opts = {
    formatters_by_ft = {
      yaml = { "prettier" },
      ["yaml.ansible"] = { "prettier" },
      json = { "prettier" },
      jsonc = { "prettier" },
      markdown = { "prettier" },
      python = { "ruff_format" },
      terraform = { "terraform_fmt" },
      tf = { "terraform_fmt" },
      lua = { "stylua" },
      sh = { "shfmt" },
      bash = { "shfmt" },
    },
    format_on_save = {
      timeout_ms = 1000,
      lsp_fallback = true,
    },
  },
}
