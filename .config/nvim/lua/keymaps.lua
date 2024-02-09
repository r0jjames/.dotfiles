vim.keymap.set("i", "jj", "<Esc>", { noremap = false })
vim.keymap.set("i", "kk", "<Esc>", { noremap = false })
-- vim.keymap.set("i", "<C-j>", "<Down>", { noremap = false })
-- vim.keymap.set("i", "<C-k>", "<Up>", { noremap = false })
-- vim.keymap.set("i", "<C-h>", "<Left>", { noremap = false })
-- vim.keymap.set("i", "<C-l>", "<Right>", { noremap = false })
-- buffers
vim.keymap.set("n", "bk", ":blast<enter>", { noremap = false })
vim.keymap.set("n", "bj", ":bfirst<enter>", { noremap = false })
vim.keymap.set("n", "bh", ":bprev<enter>", { noremap = false })
vim.keymap.set("n", "bl", ":bnext<enter>", { noremap = false })
vim.keymap.set("n", "bd", ":bdelete<enter>", { noremap = false })
--files
vim.keymap.set("n", "QQ", ":q!<CR>", {})
vim.keymap.set("n", "QA", ":qa!<CR>", {})
vim.keymap.set("n", "WW", ":w!<CR>", {})
vim.keymap.set("n", "E", "$", {})
--splits
vim.keymap.set("n", "<C-W>,", ":vertical resize -10<CR><CR>", {})
vim.keymap.set("n", "<C-W>.", ":vertical resize +10<CR>", {})
-- Options through Telescope
vim.keymap.set("n", "<Leader><tab>", "<Cmd>lua require('telescope.builtin').commands()<CR>", { noremap = false })
vim.keymap.set("n", "<C-f>",
  "<cmd>Telescope current_buffer_fuzzy_find sorting_strategy=ascending prompt_position=top<CR>")
vim.keymap.set("n", "<leader>stt", ":TodoTelescope<CR>", {})
-- Go
vim.keymap.set({ 'n', 'i' }, '<C-1>', '<Cmd>:w!<bar> GoRun -F<enter>', { noremap = false })
-- [[ Basic Keymaps ]] -- Keymaps for better default experience
-- See `:help vim.keymap.set()`
vim.keymap.set({ 'n', 'v' }, '<Space>', '<Nop>', { silent = true })
-- Remap for dealing with word wrap
vim.keymap.set('n', 'k', "v:count == 0 ? 'gk' : 'k'", { expr = true, silent = true })
vim.keymap.set('n', 'j', "v:count == 0 ? 'gj' : 'j'", { expr = true, silent = true })
-- Diagnostic keymaps
vim.keymap.set('n', '[d', vim.diagnostic.goto_prev, { desc = 'Go to previous diagnostic message' })
vim.keymap.set('n', ']d', vim.diagnostic.goto_next, { desc = 'Go to next diagnostic message' })
vim.keymap.set('n', '<leader>e', vim.diagnostic.open_float, { desc = 'Open floating diagnostic message' })
vim.keymap.set('n', '<leader>q', vim.diagnostic.setloclist, { desc = 'Open diagnostics list' })
-- Toggle Term
-- vim.keymap.set({ 'n', 'i' }, '<C-]>', '<cmd>:ToggleTerm size=60 dir=. direction=vertical<CR>', { noremap = false })
-- Neotree
--vim.keymap.set("n", "<C-n>", ":Neotree filesystem reveal left<CR>", {})
vim.keymap.set("n", "<C-n>", ":Neotree float<CR>", {})
vim.keymap.set("n", "<leader>bf", ":Neotree buffers reveal float<CR>", {})
