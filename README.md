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
| `:CR`   | Open the CodeRabbit buffer |

## Requirements

- Vim 8.0+ with Python 3 support (`+python3`)

## License

MIT
