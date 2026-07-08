-- =============================
-- Linting: nvim-lint (diagnostics on save + leaving insert)
-- =============================
return {
  "mfussenegger/nvim-lint",
  event = { "BufReadPre", "BufNewFile" },
  config = function()
    local lint = require("lint")

    lint.linters_by_ft = {
      yaml = { "yamllint" },
      ["yaml.ansible"] = { "ansible_lint" },
      dockerfile = { "hadolint" },
      terraform = { "tflint" },
    }

    -- Relax yamllint so learning-phase YAML isn't buried in style noise.
    local yamllint = lint.linters.yamllint
    yamllint.args = {
      "--format",
      "parsable",
      "-d",
      "{extends: relaxed, rules: {line-length: disable, document-start: disable}}",
      "-",
    }

    local grp = vim.api.nvim_create_augroup("NvimLint", { clear = true })
    vim.api.nvim_create_autocmd({ "BufWritePost", "InsertLeave", "BufReadPost" }, {
      group = grp,
      callback = function()
        -- Only lint modifiable, real files
        if vim.bo.modifiable and vim.bo.buftype == "" then
          lint.try_lint()
        end
      end,
    })
  end,
}
