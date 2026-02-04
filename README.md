# vim4rabbit

Easily perform code reviews with CodeRabbit directly in Vim.

## Installation

### Using Vundle

1. Add the following line to your `~/.vimrc` between `call vundle#begin()` and `call vundle#end()`:

```vim
Plugin 'davidpthomas/vim4rabbit'
```

2. Save the file and run:

```vim
:source %
:PluginInstall
```

Or restart Vim and run `:PluginInstall`.

### Manual Installation

Clone the repository into your Vim bundle directory:

```bash
git clone https://github.com/davidpthomas/vim4rabbit.git ~/.vim/bundle/vim4rabbit
```

## Usage

| Command | Description |
|---------|-------------|
| `:Rabbit`   | Open the CodeRabbit buffer |

## Requirements

- Vim 8.0+ with Python 3 support (`+python3`)
- CodeRabbit CLI (see setup below)

## CodeRabbit CLI Setup

### Installation

Install the CodeRabbit CLI:

```bash
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
```

Restart your shell or reload your configuration:

```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Authentication

Connect your CodeRabbit account:

```bash
coderabbit auth login
```

Follow the browser prompt to authenticate and paste your access token back into the CLI.

### Verify Installation

Test the CLI is working:

```bash
coderabbit --help
```

### CLI Usage

| Command | Description |
|---------|-------------|
| `coderabbit` | Launch interactive code review |
| `coderabbit --plain` | Plain text output |
| `coderabbit --base <branch>` | Specify base branch |
| `cr` | Short alias for `coderabbit` |

For more information, see the [CodeRabbit CLI documentation](https://docs.coderabbit.ai/cli/overview).

## License

MIT
