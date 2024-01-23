vim.keymap.set("i", "jj", "<Esc>", { noremap = false })
vim.keymap.set("i", "kk", "<Esc>", { noremap = false })
vim.keymap.set("n", "<leader>stt", ":TodoTelescope<CR>", {})
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

-- Go
vim.keymap.set({ 'n', 'i' }, '<C-1>', '<Cmd>:w!<bar> GoRun -F<enter>', { noremap = false })
