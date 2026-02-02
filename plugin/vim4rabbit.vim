" vim4rabbit - A Vim plugin powered by Python
" Maintainer: vim4rabbit
" License: MIT

if exists('g:loaded_vim4rabbit')
    finish
endif
let g:loaded_vim4rabbit = 1

" Check for Python3 support
if !has('python3')
    echohl ErrorMsg
    echom 'vim4rabbit requires Vim compiled with +python3'
    echohl None
    finish
endif

" Initialize Python module
" Add pythonx directory to Python path and import vim4rabbit
let s:plugin_root = expand('<sfile>:p:h:h')
python3 << EOF
import sys
import vim

# Add plugin's pythonx directory to Python path
plugin_root = vim.eval('s:plugin_root')
pythonx_path = plugin_root + '/pythonx'
if pythonx_path not in sys.path:
    sys.path.insert(0, pythonx_path)

# Import vim4rabbit module
import vim4rabbit
EOF

" Define the :Rabbit command with optional subcommands
command! -nargs=? -complete=customlist,vim4rabbit#CompleteRabbit Rabbit call vim4rabbit#Rabbit(<q-args>)
