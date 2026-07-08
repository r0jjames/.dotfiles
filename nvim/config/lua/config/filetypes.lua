-- =============================
-- Filetype detection + per-filetype tweaks
-- =============================
-- Route Ansible-convention paths to the `yaml.ansible` filetype so the
-- ansible-language-server + ansible-lint attach there, while plain k8s /
-- docker-compose YAML stays `yaml` for yaml-language-server + SchemaStore.

vim.filetype.add({
  pattern = {
    -- playbooks/  and  roles/<name>/{tasks,handlers,meta}/*.yml
    [".*/playbooks/.*%.ya?ml"] = "yaml.ansible",
    [".*/roles/.*/tasks/.*%.ya?ml"] = "yaml.ansible",
    [".*/roles/.*/handlers/.*%.ya?ml"] = "yaml.ansible",
    [".*/roles/.*/meta/.*%.ya?ml"] = "yaml.ansible",
    -- variable + inventory dirs
    [".*/group_vars/.*%.ya?ml"] = "yaml.ansible",
    [".*/host_vars/.*%.ya?ml"] = "yaml.ansible",
    [".*/inventories/.*%.ya?ml"] = "yaml.ansible",
    -- filename fallbacks
    [".*/playbook%.ya?ml"] = "yaml.ansible",
    [".*/site%.ya?ml"] = "yaml.ansible",
    [".*%.ansible%.ya?ml"] = "yaml.ansible",
  },
})

-- Ensure Helm template files are treated as helm (not yaml) when detected as such.
-- Helm's Go-template syntax breaks yaml-ls; helm_ls handles it.
vim.filetype.add({
  pattern = {
    [".*/templates/.*%.tpl"] = "helm",
    [".*/templates/.*%.ya?ml"] = "helm",
    ["helmfile.*%.ya?ml"] = "helm",
  },
})

-- Two-space indent for the DevOps filetypes (YAML demands it).
local grp = vim.api.nvim_create_augroup("DevOpsIndent", { clear = true })
vim.api.nvim_create_autocmd("FileType", {
  group = grp,
  pattern = { "yaml", "yaml.ansible", "helm", "json", "terraform", "dockerfile", "lua" },
  callback = function()
    vim.bo.expandtab = true
    vim.bo.tabstop = 2
    vim.bo.shiftwidth = 2
    vim.bo.softtabstop = 2
  end,
})

-- Python conventionally uses 4 spaces.
vim.api.nvim_create_autocmd("FileType", {
  group = grp,
  pattern = { "python" },
  callback = function()
    vim.bo.tabstop = 4
    vim.bo.shiftwidth = 4
    vim.bo.softtabstop = 4
  end,
})
