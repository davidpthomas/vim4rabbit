# Contributing to vim4rabbit

Thank you for your interest in contributing! vim4rabbit is a Vim plugin and we want to keep it working cleanly in standard Vim (not Neovim).

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Run the test suite (see below)
6. Push your branch and open a pull request against `main`

## Requirements

- Vim 8.0+ with `+python3`
- Python 3.8+
- CodeRabbit CLI (for integration testing)

## Running Tests

```bash
python -m pytest tests/ -v
```

With coverage:

```bash
.venv/bin/python -m pytest tests/ --cov=vim4rabbit --cov-report=term-missing
```

## Guidelines

- Keep changes compatible with standard Vim — no Neovim-only APIs
- Python code lives in `pythonx/vim4rabbit/`; UI/buffer code lives in `autoload/vim4rabbit.vim`
- Add tests for new Python logic in `tests/`
- Keep PRs focused — one feature or fix per PR

## Reporting Issues

Open an issue on GitHub with steps to reproduce, your Vim version (`:version`), and OS.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
