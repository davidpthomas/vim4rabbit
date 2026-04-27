# Changelog

All notable changes to vim4rabbit will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [0.6.0] - 2026-04-26

### Added
- OSS compliance: LICENSE (MIT), CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md
- vim-plug installation instructions and prerequisites in README

## [0.5.0] - 2026-02

### Added
- Snake vs Rabbit! mini-game with enemy snake, skulls, WASD/hjkl controls
- Matrix digital rain mini-game with toggleable character sets
- Global Thermonuclear War (WarGames tribute) mini-game with chessboard result screen
- Pong mini-game with human vs AI paddle
- Mini-games accessible via `p` during loading; cancel returns to game menu
- Mini-game keeps running when review job completes in background

### Changed
- Renamed Snake game to "Snake vs Rabbit!", hotkey to `s`
- Game menu centered; uniform `[c]` cancel UX across all games and buffers
- Zen Spiral speed increased 25%

## [0.4.0] - 2026-01

### Added
- Claude Code CLI integration: select issues and launch Claude with `@`
- Issue selection with checkboxes; select all (`\a`) / deselect all (`\n`)
- Elapsed timer during review with total time shown in results
- Close confirmation when leaving a review results buffer
- Word wrap enabled in review results buffer

### Changed
- Simplified help menu hotkeys (removed `r` prefix)
- Only show `[c]` close keybinding when no issues are found
- Execution buffer keybindings fixed: `[c]` closes, `[@]` launches Claude
- Review buffer renamed from `[Scratch]` to `Rabbit Review` with branch context

### Fixed
- False positive preamble issue parsing
- py3eval encoding issue in close confirmation

## [0.3.0] - 2025-12

### Added
- Coffee Break! and Zen Spiral mini-games playable during loading (`p` to open menu)
- `review all` command for committed + uncommitted changes combined
- `review committed` command for committed-only changes
- "No changes" jumping rabbit animation
- 100% test coverage across all modules; pytest + coverage reporting

### Changed
- Replaced braille spinner with animated rabbit eating vegetables
- Refactored VimScript logic to Python backend (`pythonx/vim4rabbit/`)
- Async review execution with cancel support

### Fixed
- CodeRabbit CLI output parsing (quote escaping)
- Preamble filtering to remove false positives from review results

## [0.2.0] - 2025-11

### Added
- Interactive review results with collapsible folds per issue
- Async job execution with animated loading indicator
- Python backend with `cli.py`, `parser.py`, `content.py`, `selection.py`
- Architecture diagram and data flow documentation in README
- Docker-based development environment (`dev/`)
- pytest testing framework

### Changed
- Refactored from pure VimScript to layered VimScript + Python architecture
- Renamed `r` command to `ru` for uncommitted review

## [0.1.0] - 2025-10

### Added
- Initial plugin scaffolding: `plugin/vim4rabbit.vim`, `autoload/vim4rabbit.vim`
- `:Rabbit` command with help screen
- CodeRabbit CLI integration for uncommitted changes review
- Raw review output displayed in a split buffer
- Docker dev environment and `.vimrc` example config
- CodeRabbit CLI setup and authentication instructions in README
