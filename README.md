# dotfiles

Personal macOS development environment managed with [GNU Stow](https://www.gnu.org/software/stow/).

## Quick Start

```bash
# Clone
git clone https://github.com/jaehanbyun/dotfiles.git ~/dotfiles
cd ~/dotfiles

# Install dependencies
brew bundle --file=Brewfile

# Deploy symlinks
stow .
```

## What's Included

### Shell
- **Zsh** with Oh-My-Zsh + Powerlevel10k theme
- Custom aliases and functions in `.zsh.after/`
- Pyenv, NVM, SDKMAN for language version management

### Terminal Emulators
- **Ghostty** (primary) — Solarized Light, Hack Nerd Font + Sarasa Fixed K
- **Alacritty** — Dracula theme
- **Kitty**, **WezTerm** — alternative configs

### Editors
- **Neovim** (LazyVim) — Solarized Light, 60+ plugins
- **Vim** — Vundle-based config
- **IdeaVim** — IntelliJ Vim emulation with 50+ IDE mappings
- **Zed** — Gruvbox Dark, Vim mode

### Window Management
- **AeroSpace** — tiling WM with vim-like navigation (Alt+HJKL)
- **skhd** — Hyper Key (Caps Lock) app launcher
- **SketchyBar** — custom macOS status bar
- **Yabai**, **Rectangle**, **Hammerspoon** — alternatives

### Input
- **Karabiner-Elements**
  - Caps Lock → Hyper Key (Ctrl+Shift+Cmd+Option) for app switching
  - Ctrl+C auto-switches Korean → English → sends interrupt → restores Korean
  - Right Command → input source toggle (Korean/English)
  - ₩ → backtick swap in Korean mode
  - Shift+Space → F18 (input source switch)

### Terminal Multiplexer
- **tmux** — Ctrl-A prefix, vim keybindings, Catppuccin theme, resurrect + continuum

### Git
- Delta diff viewer (side-by-side, GitHub theme)
- 30+ aliases (`co`, `nb`, `amend`, `recent-branches`, etc.)
- Pull strategy: rebase
- Default branch: main

### Claude Code
- Global `CLAUDE.md` with session management, coding principles, work patterns
- Custom skills: daily/weekly/monthly work logger, obsidian integrations
- Custom agents: 20+ specialized agents
- Aliases: `clc` (continue), `cld` (bypass permissions), `clcd` (both)

## Directory Structure

```
~/dotfiles/
├── .config/
│   ├── aerospace/      # tiling window manager
│   ├── ghostty/        # primary terminal
│   ├── karabiner/      # keyboard remapping
│   ├── lazy-nvim/      # neovim (LazyVim)
│   ├── sketchybar/     # status bar
│   ├── skhd/           # hotkey daemon
│   └── ...             # alacritty, kitty, yazi, zed, etc.
├── .zsh.after/
│   ├── base.zsh        # base shell config
│   └── byeonjaehan.zsh # personal overrides
├── .zshrc              # shell entry point
├── .gitconfig          # git config (user info via include)
├── .tmux.conf          # tmux config
├── Brewfile            # homebrew packages (180+)
└── CLAUDE.md           # project-level claude instructions
```

## Stow Usage

```bash
# Deploy all dotfiles
stow .

# Re-deploy after changes
stow -R .

# Remove symlinks
stow -D .
```

## Credits

Initially inspired by [msbaek/dotfiles](https://github.com/msbaek/dotfiles).
