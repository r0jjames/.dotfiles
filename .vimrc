"
" " Show cursor position.
" set ruler
" " Show incomplete command.
" set showcmd
" " Show a menu when using tab completion.
" set wildmenu
"
" set scrolloff=5
"
" set hlsearch
" set incsearch
" set ignorecase
" set smartcase
" "Turn on line numbering
" set number
" set backup
" lua <<EOF
" local format_sync_grp = vim.api.nvim_create_augroup("GoFormat", {})
" vim.api.nvim_create_autocmd("BufWritePre", {
"   pattern = "*.go",
"   callback = function()
"    require('go.format').goimport()
"   end,
"   group = format_sync_grp,
" })
"
" EOF

set autoindent expandtab tabstop=2 shiftwidth=2

