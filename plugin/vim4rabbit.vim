" vim4rabbit - A Vim plugin powered by Python
" Maintainer: vim4rabbit
" License: MIT

if exists('g:loaded_vim4rabbit')
    finish
endif
let g:loaded_vim4rabbit = 1

" Define the :CR command
command! CR call vim4rabbit#OpenRabbitBuffer()

" Define the :Rabbit command with subcommands
command! -nargs=1 -complete=customlist,vim4rabbit#CompleteRabbit Rabbit call vim4rabbit#Rabbit(<f-args>)
