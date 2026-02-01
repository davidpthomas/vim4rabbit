" vim4rabbit autoload functions
" These functions are loaded on-demand when called

function! vim4rabbit#OpenRabbitBuffer()
    " Open a new horizontal split
    new

    " Set buffer options
    setlocal buftype=nofile
    setlocal bufhidden=wipe
    setlocal noswapfile
    setlocal nobuflisted
    setlocal filetype=vim4rabbit

    " Add content
    call setline(1, 'All your vim are belong to us.')

    " Make buffer read-only
    setlocal nomodifiable
endfunction
