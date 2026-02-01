" vim4rabbit - A Vim plugin powered by Python
" Maintainer: vim4rabbit
" License: MIT

if exists('g:loaded_vim4rabbit')
    finish
endif
let g:loaded_vim4rabbit = 1

" Define commands
command! CR call vim4rabbit#OpenRabbitBuffer()
command! CRTest call vim4rabbit#TestIndicator()
command! CRReview call vim4rabbit#RunCodeRabbit()

" Set up statusline to include vim4rabbit spinner
" Users can customize by setting g:vim4rabbit_statusline = 0
if get(g:, 'vim4rabbit_statusline', 1)
    if &statusline == ''
        set statusline=%f\ %m%r%h%w%=%{vim4rabbit#GetStatusLine()}\ %l,%c\ %P
    else
        set statusline+=%{vim4rabbit#GetStatusLine()}
    endif
endif
