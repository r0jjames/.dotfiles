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

-- Leader must be set before lazy + keymaps
vim.g.mapleader = " "
vim.g.maplocalleader = " "

-- =============================
-- Core config (order matters: filetypes before plugins attach LSP)
-- =============================
require("config.options")
require("config.filetypes")
require("config.keymaps")

-- =============================
-- Plugins (each file in lua/plugins/ returns a lazy spec)
-- =============================
require("lazy").setup({
  { import = "plugins" },
}, {
  change_detection = { notify = false },
})
