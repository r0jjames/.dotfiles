-- =============================
-- Global key mappings
-- (LSP-buffer maps live in config/lsp.lua on attach)
-- =============================
local map = vim.keymap.set

-- File explorer
map("n", "<leader>e", ":Neotree toggle<CR>", { desc = "Toggle file explorer", silent = true })

-- Diagnostics navigation
map("n", "[d", vim.diagnostic.goto_prev, { desc = "Prev diagnostic" })
map("n", "]d", vim.diagnostic.goto_next, { desc = "Next diagnostic" })
map("n", "<leader>d", vim.diagnostic.open_float, { desc = "Line diagnostics" })

-- Clear search highlight
map("n", "<Esc>", ":nohlsearch<CR>", { silent = true })
