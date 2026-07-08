-- =============================
-- Treesitter: syntax highlighting + indentation for the DevOps stack
-- Pinned to the stable `master` branch (the `main` rewrite has a different API).
-- =============================
return {
  "nvim-treesitter/nvim-treesitter",
  branch = "master",
  build = ":TSUpdate",
  event = { "BufReadPost", "BufNewFile" },
  config = function()
    require("nvim-treesitter.configs").setup({
      ensure_installed = {
        "yaml",
        "dockerfile",
        "python",
        "hcl", -- terraform
        "terraform",
        "bash",
        "lua",
        "json",
        "jsonc",
        "markdown",
        "markdown_inline",
        "gitignore",
      },
      auto_install = true,
      highlight = { enable = true },
      indent = { enable = true },
    })
  end,
}
