-- =============================
-- Shared LSP helpers: capabilities, on_attach keymaps, diagnostics UI
-- Consumed by lua/plugins/lsp.lua
-- =============================
local M = {}

-- Completion capabilities from nvim-cmp
function M.capabilities()
  local ok, cmp_lsp = pcall(require, "cmp_nvim_lsp")
  if ok then
    return cmp_lsp.default_capabilities()
  end
  return vim.lsp.protocol.make_client_capabilities()
end

-- Buffer-local keymaps applied when any server attaches
function M.on_attach(_, bufnr)
  local function nmap(lhs, rhs, desc)
    vim.keymap.set("n", lhs, rhs, { buffer = bufnr, silent = true, desc = desc })
  end

  nmap("gd", vim.lsp.buf.definition, "Go to definition")
  nmap("gr", vim.lsp.buf.references, "References")
  nmap("K", vim.lsp.buf.hover, "Hover docs")
  nmap("<leader>rn", vim.lsp.buf.rename, "Rename symbol")
  nmap("<leader>ca", vim.lsp.buf.code_action, "Code action")
end

-- Diagnostics presentation (call once at startup)
function M.setup_diagnostics()
  vim.diagnostic.config({
    virtual_text = { spacing = 2, prefix = "●" },
    signs = true,
    underline = true,
    update_in_insert = false,
    severity_sort = true,
    float = { border = "rounded", source = true },
  })
end

return M
