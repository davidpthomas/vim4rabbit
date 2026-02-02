" vim4rabbit autoload functions
" These functions are loaded on-demand when called
"
" Architecture: This file contains UI/buffer operations only.
" All logic (parsing, CLI execution, caching) is in Python (pythonx/vim4rabbit/).

" Store buffer numbers for reference
let s:help_bufnr = -1
let s:review_bufnr = -1

" Token usage tracking
" Initialize with defaults; updated by API calls or cache file
let g:vim4rabbit_tokens = {'used': 0, 'limit': 0, 'provider': 'rabbit'}

" Statusline component - returns formatted token usage for far-right display
" Usage: set statusline+=%{vim4rabbit#Statusline()}
function! vim4rabbit#Statusline()
    let l:t = g:vim4rabbit_tokens
    if l:t.limit == 0
        return ''
    endif

    let l:pct = (l:t.used * 100) / l:t.limit

    " Format: 🐰 45% or with warning threshold
    if l:pct >= 90
        return '%#ErrorMsg#🐰 ' . l:pct . '%%%*'
    elseif l:pct >= 75
        return '%#WarningMsg#🐰 ' . l:pct . '%%%*'
    endif
    return '🐰 ' . l:pct . '%'
endfunction

" Detailed statusline with token counts (alternative format)
function! vim4rabbit#StatuslineVerbose()
    let l:t = g:vim4rabbit_tokens
    if l:t.limit == 0
        return ''
    endif

    let l:used_k = l:t.used / 1000
    let l:limit_k = l:t.limit / 1000
    let l:pct = (l:t.used * 100) / l:t.limit

    return printf('🐰 %dk/%dk (%d%%)', l:used_k, l:limit_k, l:pct)
endfunction

" Update token usage from cache file (~/.vim4rabbit/usage.json)
function! vim4rabbit#LoadTokenUsage()
    let l:data = py3eval('vim4rabbit.vim_load_cached_usage()')
    let g:vim4rabbit_tokens.used = l:data.used
    let g:vim4rabbit_tokens.limit = l:data.limit
    let g:vim4rabbit_tokens.provider = l:data.provider
    redrawstatus
endfunction

" Set token usage directly (call from API response handlers)
function! vim4rabbit#SetTokenUsage(used, limit, ...)
    let l:provider = a:0 > 0 ? a:1 : 'rabbit'
    let l:data = py3eval('vim4rabbit.vim_set_usage(' . a:used . ', ' . a:limit . ', "' . l:provider . '")')
    let g:vim4rabbit_tokens.used = l:data.used
    let g:vim4rabbit_tokens.limit = l:data.limit
    let g:vim4rabbit_tokens.provider = l:data.provider
    redrawstatus
endfunction

" Start polling for token usage updates (optional)
function! vim4rabbit#StartTokenPolling(interval_ms)
    call vim4rabbit#LoadTokenUsage()
    call timer_start(a:interval_ms, {-> vim4rabbit#LoadTokenUsage()}, {'repeat': -1})
endfunction

" Main Rabbit command dispatcher
function! vim4rabbit#Rabbit(subcmd)
    let l:cmd = a:subcmd

    " Default to 'help' if no subcommand provided
    if l:cmd ==# ''
        let l:cmd = 'help'
    endif

    if l:cmd ==# 'help'
        call vim4rabbit#Help()
    elseif l:cmd ==# 'review'
        call vim4rabbit#Review()
    else
        echo "Unknown rabbit command: " . l:cmd
        echo "Available commands: help, review"
    endif
endfunction

" Command completion for :Rabbit
function! vim4rabbit#CompleteRabbit(ArgLead, CmdLine, CursorPos)
    let l:commands = ['help', 'review']
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

    " Map keybindings for help buffer
    nnoremap <buffer> <silent> q :call vim4rabbit#CloseHelp()<CR>
    nnoremap <buffer> <silent> r :call vim4rabbit#Review()<CR>

    " Auto-resize on window resize
    augroup vim4rabbit_help_resize
        autocmd!
        autocmd VimResized * call vim4rabbit#ResizeHelp()
    augroup END

    " Clean up when buffer is wiped
    autocmd BufWipeout <buffer> call vim4rabbit#CleanupHelp()
endfunction

" Render the help screen content with 3-column layout (via Python)
function! vim4rabbit#RenderHelp()
    let l:width = winwidth(0)
    let l:content = py3eval('vim4rabbit.vim_render_help(' . l:width . ')')

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

" Open the review buffer on the right side of the screen
function! vim4rabbit#Review()
    " If review buffer already exists, just focus it
    if s:review_bufnr != -1 && bufexists(s:review_bufnr)
        let l:winnr = bufwinnr(s:review_bufnr)
        if l:winnr != -1
            execute l:winnr . 'wincmd w'
            return
        endif
    endif

    " Open a new vertical split on the right (full column)
    execute 'botright vnew'

    " Store buffer number
    let s:review_bufnr = bufnr('%')

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
    setlocal winfixwidth

    " Show loading message (from Python)
    let l:loading = py3eval('vim4rabbit.vim_get_loading_content()')
    setlocal modifiable
    call setline(1, l:loading)
    setlocal nomodifiable
    redraw

    " Map 'q' to close the review buffer
    nnoremap <buffer> <silent> q :call vim4rabbit#CloseReview()<CR>

    " Clean up when buffer is wiped
    autocmd BufWipeout <buffer> call vim4rabbit#CleanupReview()

    " Run the review asynchronously
    call vim4rabbit#RunReview()
endfunction

" Run CodeRabbit CLI and display results (logic in Python)
function! vim4rabbit#RunReview()
    " Run review via Python
    let l:result = py3eval('vim4rabbit.vim_run_review()')

    " Fetch and update token usage after review
    if l:result.success
        call vim4rabbit#FetchTokenUsage()
    endif

    " Format output via Python
    let l:content = py3eval('vim4rabbit.vim_format_review(' .
        \ l:result.success . ', ' .
        \ string(l:result.issues) . ', ' .
        \ string(l:result.error_message) . ', ' .
        \ g:vim4rabbit_tokens.used . ', ' .
        \ g:vim4rabbit_tokens.limit . ')')

    " Update buffer content
    if s:review_bufnr != -1 && bufexists(s:review_bufnr)
        let l:winnr = bufwinnr(s:review_bufnr)
        if l:winnr != -1
            let l:cur_winnr = winnr()
            execute l:winnr . 'wincmd w'
            setlocal modifiable
            " Clear buffer and add new content
            silent! %delete _
            call setline(1, l:content)
            setlocal nomodifiable
            " Move cursor to top
            normal! gg
            redraw
        endif
    endif
endfunction

" Fetch token usage from CodeRabbit CLI (via Python)
function! vim4rabbit#FetchTokenUsage()
    let l:data = py3eval('vim4rabbit.vim_fetch_usage()')
    let g:vim4rabbit_tokens.used = l:data.used
    let g:vim4rabbit_tokens.limit = l:data.limit
    let g:vim4rabbit_tokens.provider = l:data.provider
    redrawstatus
endfunction

" Close the review buffer
function! vim4rabbit#CloseReview()
    if s:review_bufnr != -1 && bufexists(s:review_bufnr)
        execute 'bwipeout ' . s:review_bufnr
    endif
endfunction

" Clean up when review buffer is closed
function! vim4rabbit#CleanupReview()
    let s:review_bufnr = -1
endfunction
