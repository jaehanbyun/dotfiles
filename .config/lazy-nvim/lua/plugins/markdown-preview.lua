return {
  {
    "iamcco/markdown-preview.nvim",
    lazy = false,
    ft = { "markdown" },
    build = function()
      vim.fn["mkdp#util#install"]()
    end,
    init = function()
      vim.g.mkdp_command_for_global = 1
      vim.g.mkdp_filetypes = { "markdown" }
      vim.g.mkdp_theme = ""
    end,
  },
}
