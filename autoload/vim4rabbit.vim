" vim4rabbit autoload functions
" These functions are loaded on-demand when called

" Store the help buffer number for reference
let s:help_bufnr = -1

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

" Main Rabbit command dispatcher
function! vim4rabbit#Rabbit(subcmd)
    if a:subcmd ==# 'help'
        call vim4rabbit#Help()
    else
        echo "Unknown rabbit command: " . a:subcmd
        echo "Available commands: help"
    endif
endfunction

" Command completion for :Rabbit
function! vim4rabbit#CompleteRabbit(ArgLead, CmdLine, CursorPos)
    let l:commands = ['help']
    return filter(l:commands, 'v:val =~ "^" . a:ArgLead')
endfunction

" Open the help buffer at the bottom of the screen
function! vim4rabbit#Help()
    " If help buffer already exists, just focus it
    if s:help_bufnr != -1 && bufexists(s:help_bufnr)
        let l:winnr = bufwinnr(s:help_bufnr)
        if l:winnr != -1
            execute l:winnr . 'wincmd w'
            return
        endif
    endif

    " Calculate 20% of total window height
    let l:height = float2nr(&lines * 0.2)
    if l:height < 5
        let l:height = 5
    endif

    " Open a new split at the bottom
    execute 'botright ' . l:height . 'new'

    " Store buffer number
    let s:help_bufnr = bufnr('%')

    " Set buffer options
    setlocal buftype=nofile
    setlocal bufhidden=wipe
    setlocal noswapfile
    setlocal nobuflisted
    setlocal filetype=vim4rabbit
    setlocal nocursorline
    setlocal nocursorcolumn
    setlocal nonumber
    setlocal norelativenumber
    setlocal signcolumn=no
    setlocal winfixheight

    " Build help content
    let l:content = []
    call add(l:content, '')
    call add(l:content, '  vim4rabbit Help')
    call add(l:content, '  ───────────────')
    call add(l:content, '')
    call add(l:content, '  Commands:')
    call add(l:content, '    r  - Review code with CodeRabbit')
    call add(l:content, '    q  - Quit this help screen')
    call add(l:content, '')
    call add(l:content, '  🐰 Happy coding with your rabbit friend! 🥕')

    " Add content to buffer
    setlocal modifiable
    call setline(1, l:content)
    setlocal nomodifiable

    " Map 'q' to close the help buffer
    nnoremap <buffer> <silent> q :call vim4rabbit#CloseHelp()<CR>

    " Auto-resize on window resize
    augroup vim4rabbit_help_resize
        autocmd!
        autocmd VimResized * call vim4rabbit#ResizeHelp()
    augroup END

    " Clean up when buffer is wiped
    autocmd BufWipeout <buffer> call vim4rabbit#CleanupHelp()
endfunction

" Close the help buffer
function! vim4rabbit#CloseHelp()
    if s:help_bufnr != -1 && bufexists(s:help_bufnr)
        execute 'bwipeout ' . s:help_bufnr
    endif
endfunction

" Resize help buffer to maintain 20% height
function! vim4rabbit#ResizeHelp()
    if s:help_bufnr == -1 || !bufexists(s:help_bufnr)
        return
    endif

    let l:winnr = bufwinnr(s:help_bufnr)
    if l:winnr == -1
        return
    endif

    let l:height = float2nr(&lines * 0.2)
    if l:height < 5
        let l:height = 5
    endif

    execute l:winnr . 'wincmd w'
    execute 'resize ' . l:height
    wincmd p
endfunction

" Clean up when help buffer is closed
function! vim4rabbit#CleanupHelp()
    let s:help_bufnr = -1
    augroup vim4rabbit_help_resize
        autocmd!
    augroup END
endfunction
