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

    " Calculate 20% of total window height (fixed at 5 lines for compact display)
    let l:height = float2nr(&lines * 0.2)
    if l:height < 5
        let l:height = 5
    endif
    if l:height > 5
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

    " Render help content
    call vim4rabbit#RenderHelp()

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

" Render the help screen content with 3-column layout
function! vim4rabbit#RenderHelp()
    let l:width = winwidth(0)
    let l:col_width = (l:width - 4) / 3

    " Commands organized by column (each column can have multiple rows)
    " Format: [key, description]
    let l:col1 = [['r', 'Review']]
    let l:col2 = []
    let l:col3 = []

    " Build the content lines
    let l:content = []

    " Header line with emoji
    call add(l:content, '  🐰 vim4rabbit Help')
    call add(l:content, '')

    " Calculate max rows needed across all columns
    let l:max_rows = max([len(l:col1), len(l:col2), len(l:col3), 1])

    " Build command rows (3 columns)
    for l:row in range(l:max_rows)
        let l:line = '  '

        " Column 1
        if l:row < len(l:col1)
            let l:cmd = l:col1[l:row]
            let l:cell = '[' . l:cmd[0] . '] ' . l:cmd[1]
        else
            let l:cell = ''
        endif
        let l:line .= l:cell . repeat(' ', l:col_width - len(l:cell))

        " Column 2
        if l:row < len(l:col2)
            let l:cmd = l:col2[l:row]
            let l:cell = '[' . l:cmd[0] . '] ' . l:cmd[1]
        else
            let l:cell = ''
        endif
        let l:line .= l:cell . repeat(' ', l:col_width - len(l:cell))

        " Column 3
        if l:row < len(l:col3)
            let l:cmd = l:col3[l:row]
            let l:cell = '[' . l:cmd[0] . '] ' . l:cmd[1]
        else
            let l:cell = ''
        endif
        let l:line .= l:cell

        call add(l:content, l:line)
    endfor

    " Bottom line with quit on the right
    let l:quit_text = '[q] Quit'
    let l:padding = l:width - len(l:quit_text) - 4
    call add(l:content, repeat(' ', l:padding) . l:quit_text . '  ')

    " Add content to buffer
    setlocal modifiable
    call setline(1, l:content)
    setlocal nomodifiable
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
    if l:height > 5
        let l:height = 5
    endif

    let l:cur_winnr = winnr()
    execute l:winnr . 'wincmd w'
    execute 'resize ' . l:height
    " Re-render to adjust column widths
    call vim4rabbit#RenderHelp()
    execute l:cur_winnr . 'wincmd w'
endfunction

" Clean up when help buffer is closed
function! vim4rabbit#CleanupHelp()
    let s:help_bufnr = -1
    augroup vim4rabbit_help_resize
        autocmd!
    augroup END
endfunction
