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
  { "catppuccin/nvim", name = "catppuccin" },

  -- File explorer
  { "nvim-neo-tree/neo-tree.nvim", branch = "v3.x", dependencies = { "nvim-lua/plenary.nvim", "nvim-tree/nvim-web-devicons", "MunifTanjim/nui.nvim" } },

  -- Status line
  { "nvim-lualine/lualine.nvim", dependencies = { "nvim-tree/nvim-web-devicons" } },

  -- Git signs
  { "lewis6991/gitsigns.nvim", dependencies = { "nvim-lua/plenary.nvim" } },

  -- LSP and autocompletion
  { "neovim/nvim-lspconfig" },
  { "hrsh7th/nvim-cmp" },
  { "hrsh7th/cmp-nvim-lsp" },
  { "L3MON4D3/LuaSnip" },
})

-- =============================
-- General settings
-- =============================
vim.opt.number = true              -- show line numbers
vim.opt.relativenumber = true      -- relative numbers
vim.opt.mouse = "a"                -- enable mouse
vim.opt.expandtab = true           -- use spaces instead of tabs
vim.opt.tabstop = 4
vim.opt.shiftwidth = 4
vim.opt.clipboard = "unnamedplus"  -- system clipboard

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

