#!/bin/bash

/Users/dt/dev/vim4rabbit/.venv/bin/python -m pytest /Users/dt/dev/vim4rabbit/tests/ -v

# Run code coverage report
/Users/dt/dev/vim4rabbit/.venv/bin/python -m pytest /Users/dt/dev/vim4rabbit/tests/ --cov=/Users/dt/dev/vim4rabbit/pythonx/vim4rabbit --cov-report=term-missing
