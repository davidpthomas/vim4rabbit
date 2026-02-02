" vim4rabbit - A Vim plugin for CodeRabbit integration
" Maintainer: vim4rabbit
" License: MIT

if exists('g:loaded_vim4rabbit')
    finish
endif
let g:loaded_vim4rabbit = 1

" Define the :Rabbit command with optional subcommands
" Usage: :Rabbit [help|review]
" Default: :Rabbit opens help
command! -nargs=? -complete=customlist,vim4rabbit#CompleteRabbit Rabbit call vim4rabbit#Rabbit(<q-args>)
