-- =============================
-- General editor settings
-- =============================
local opt = vim.opt

opt.number = true
opt.relativenumber = true
opt.mouse = "a"
opt.clipboard = "unnamedplus"

-- Indentation: 2 spaces is the norm for YAML-heavy DevOps work.
-- Per-filetype overrides live in config/filetypes.lua.
opt.expandtab = true
opt.tabstop = 2
opt.shiftwidth = 2
opt.softtabstop = 2

opt.signcolumn = "yes" -- stable gutter for gitsigns + diagnostics
opt.termguicolors = true
opt.updatetime = 300
opt.splitright = true
opt.splitbelow = true
