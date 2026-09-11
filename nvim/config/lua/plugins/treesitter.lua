-- =============================
-- Treesitter: syntax highlighting + indentation for the DevOps stack
-- Pinned to the stable `master` branch (the `main` rewrite has a different API).
-- =============================
return {
  "nvim-treesitter/nvim-treesitter",
  branch = "master",
  build = ":TSUpdate",
  event = { "BufReadPost", "BufNewFile" },
  init = function()
    -- `master` supports Neovim <= 0.11. From 0.12 a query match maps each
    -- capture to a list of nodes, while master's predicates and directives
    -- (e.g. markdown's set-lang-from-info-string!) expect one node and fail
    -- with "attempt to call method 'range'". Hand them the last node instead.
    if vim.fn.has("nvim-0.12") == 0 then
      return
    end
    local query = require("vim.treesitter.query")
    local function single_node(handler)
      return function(match, ...)
        local nodes = {}
        for id, node in pairs(match) do
          nodes[id] = type(node) == "table" and node[#node] or node
        end
        return handler(nodes, ...)
      end
    end
    for _, name in ipairs({ "add_predicate", "add_directive" }) do
      local register = query[name]
      query[name] = function(n, handler, opts)
        if type(opts) == "table" and opts.all == false then
          handler = single_node(handler)
        end
        return register(n, handler, opts)
      end
    end
  end,
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
