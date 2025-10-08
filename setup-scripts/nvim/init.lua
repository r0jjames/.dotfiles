-- =============================
-- Bootstrap lazy.nvim
-- =============================
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

-- =============================
-- Plugins
-- =============================
require("lazy").setup({
  -- Colorscheme
  { "catppuccin/nvim",           name = "catppuccin" },

  -- File explorer
  {
    "nvim-neo-tree/neo-tree.nvim",
    branch = "v3.x",
    dependencies = {
      "nvim-lua/plenary.nvim",
      "nvim-tree/nvim-web-devicons",
      "MunifTanjim/nui.nvim"
    }
  },

  -- Status line
  { "nvim-lualine/lualine.nvim", dependencies = { "nvim-tree/nvim-web-devicons" } },

  -- Git signs
  { "lewis6991/gitsigns.nvim",   dependencies = { "nvim-lua/plenary.nvim" } },

  -- LSP and autocompletion
  { "neovim/nvim-lspconfig" },
  { "hrsh7th/nvim-cmp" },
  { "hrsh7th/cmp-nvim-lsp" },
  { "L3MON4D3/LuaSnip" },

  -- Terraform support
  { "hashivim/vim-terraform" },

  -- Formatter
  { "stevearc/conform.nvim" },
})

-- =============================
-- General settings
-- =============================
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.mouse = "a"
vim.opt.expandtab = true
vim.opt.tabstop = 4
vim.opt.shiftwidth = 4
vim.opt.clipboard = "unnamedplus"

-- =============================
-- Colorscheme
-- =============================
vim.cmd([[colorscheme catppuccin]])

-- =============================
-- Key mappings for Neo-tree
-- =============================
vim.keymap.set("n", "<leader>e", ":Neotree toggle<CR>", { noremap = true, silent = true })

-- =============================
-- Lualine setup
-- =============================
require("lualine").setup({
  options = { theme = "catppuccin" },
})

-- =============================
-- Gitsigns setup
-- =============================
require("gitsigns").setup()

-- =============================
-- Terraform setup
-- =============================
vim.g.terraform_fmt_on_save = 0 -- handled by conform.nvim
vim.g.terraform_align = 1

-- =============================
-- LSP setup (New API style)
-- =============================
local capabilities = require("cmp_nvim_lsp").default_capabilities()

vim.lsp.configs = vim.lsp.configs or {}
vim.lsp.configs.terraformls = {
  default_config = {
    cmd = { "terraform-ls", "serve" },
    filetypes = { "terraform", "tf" },
    root_dir = vim.fs.dirname(vim.fs.find({ ".terraform", ".git" }, { upward = true })[1]),
    capabilities = capabilities,
    on_attach = function(_, bufnr)
      local opts = { buffer = bufnr, noremap = true, silent = true }
      vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
      vim.keymap.set("n", "K", vim.lsp.buf.hover, opts)
    end,
  },
}

if vim.fn.executable("terraform-ls") == 1 then
  vim.lsp.enable("terraformls")
else
  vim.notify("terraform-ls not found in PATH", vim.log.levels.WARN)
end

-- =============================
-- nvim-cmp setup
-- =============================
local cmp = require("cmp")

cmp.setup({
  snippet = {
    expand = function(args)
      require("luasnip").lsp_expand(args.body)
    end,
  },
  mapping = cmp.mapping.preset.insert({
    ["<C-b>"] = cmp.mapping.scroll_docs(-4),
    ["<C-f>"] = cmp.mapping.scroll_docs(4),
    ["<C-Space>"] = cmp.mapping.complete(),
    ["<C-e>"] = cmp.mapping.abort(),
    ["<CR>"] = cmp.mapping.confirm({ select = true }),
  }),
  sources = cmp.config.sources({
    { name = "nvim_lsp" },
    { name = "buffer" },
  }),
})

-- =============================
-- Conform setup (Formatter)
-- =============================
require("conform").setup({
  formatters_by_ft = {
    terraform = { "terraform_fmt" },
    tf = { "terraform_fmt" },
  },
  format_on_save = {
    timeout_ms = 1000,
    lsp_fallback = true,
  },
})
