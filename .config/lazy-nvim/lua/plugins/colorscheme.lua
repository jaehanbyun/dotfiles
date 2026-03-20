-- I manually created this file
return {
  -- Solarized Theme
  {
    "ishan9299/nvim-solarized-lua",
    lazy = false,
    priority = 1000,
    config = function()
      vim.o.background = "light"
    end,
  },
  {
    "LazyVim/LazyVim",
    opts = {
      -- Solarized Light (matches Ghostty iTerm2 Solarized Light)
      colorscheme = "solarized",
      -- Previous: github_light
      -- colorscheme = "github_light",
      -- colorscheme = "catppuccin-latte",
      -- colorscheme = "catppuccin-mocha",
      -- colorscheme = "gruvbox",
    },
  },
}
