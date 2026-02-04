" vim4rabbit autoload functions
" These functions are loaded on-demand when called
"
" Architecture: This file contains UI/buffer operations only.
" All logic (parsing, CLI execution) is in Python (pythonx/vim4rabbit/).

" Store buffer numbers for reference
let s:help_bufnr = -1
let s:review_bufnr = -1

" Store the running job for cancellation
let s:review_job = v:null
let s:review_output = []

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
    nnoremap <buffer> <silent> ru :call vim4rabbit#CloseHelp() \| call vim4rabbit#Review()<CR>

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
    setlocal nolist

    " Show loading message with cancel option
    let l:loading = py3eval('vim4rabbit.vim_get_loading_content()')
    setlocal modifiable
    call setline(1, l:loading)
    setlocal nomodifiable
    redraw

    " Map 'q' to close and 'c' to cancel
    nnoremap <buffer> <silent> q :call vim4rabbit#CloseReview()<CR>
    nnoremap <buffer> <silent> c :call vim4rabbit#CancelReview()<CR>

    " Clean up when buffer is wiped
    autocmd BufWipeout <buffer> call vim4rabbit#CleanupReview()

    " Run the review asynchronously
    call vim4rabbit#RunReviewAsync()
endfunction

" Run CodeRabbit CLI asynchronously
function! vim4rabbit#RunReviewAsync()
    " Reset output collector
    let s:review_output = []

    " Start the job
    let l:cmd = ['coderabbit', 'review', '--type', 'uncommitted', '--plain']
    let s:review_job = job_start(l:cmd, {
        \ 'out_cb': function('s:OnReviewOutput'),
        \ 'err_cb': function('s:OnReviewOutput'),
        \ 'exit_cb': function('s:OnReviewExit'),
        \ 'mode': 'raw',
        \ })

    if job_status(s:review_job) ==# 'fail'
        call s:DisplayReviewError('Failed to start coderabbit')
    endif
endfunction

" Callback for job output (stdout and stderr)
function! s:OnReviewOutput(channel, msg)
    call add(s:review_output, a:msg)
endfunction

" Callback when job exits
function! s:OnReviewExit(job, exit_status)

    " Clear the job reference
    let s:review_job = v:null

    " Check if buffer still exists
    if s:review_bufnr == -1 || !bufexists(s:review_bufnr)
        return
    endif

    " Combine output
    let l:output = join(s:review_output, '')

    " Format output via Python
    if a:exit_status != 0
        let l:content = py3eval("vim4rabbit.vim_format_review(False, [], " . json_encode(l:output) . ")")
    else
        let l:result = py3eval("vim4rabbit.vim_parse_review_output(" . json_encode(l:output) . ")")
        let l:content = py3eval('vim4rabbit.vim_format_review(' .
            \ l:result.success . ', ' .
            \ string(l:result.issues) . ', ' .
            \ string(l:result.error_message) . ')')
    endif

    " Update buffer content
    call s:UpdateReviewBuffer(l:content)
endfunction

" Cancel the running review and close buffer
function! vim4rabbit#CancelReview()
    if s:review_job != v:null && job_status(s:review_job) ==# 'run'
        call job_stop(s:review_job, 'kill')
        let s:review_job = v:null
    endif

    " Close the buffer
    if s:review_bufnr != -1 && bufexists(s:review_bufnr)
        execute 'bwipeout ' . s:review_bufnr
    endif
endfunction

" Update the review buffer with content
function! s:UpdateReviewBuffer(content)
    if s:review_bufnr == -1 || !bufexists(s:review_bufnr)
        return
    endif

    let l:winnr = bufwinnr(s:review_bufnr)
    if l:winnr == -1
        return
    endif

    let l:cur_winnr = winnr()
    execute l:winnr . 'wincmd w'
    setlocal modifiable
    " Clear buffer and add new content
    silent! %delete _
    call setline(1, a:content)
    setlocal nomodifiable
    " Move cursor to top
    normal! gg

    " Remove cancel mapping since job is done
    silent! nunmap <buffer> c

    execute l:cur_winnr . 'wincmd w'
    redraw
endfunction

" Display an error in the review buffer
function! s:DisplayReviewError(message)
    let l:content = py3eval('vim4rabbit.vim_format_review(False, [], ' . string(a:message) . ')')
    call s:UpdateReviewBuffer(l:content)
endfunction

" Close the review buffer
function! vim4rabbit#CloseReview()
    " Cancel any running job first
    if s:review_job != v:null && job_status(s:review_job) ==# 'run'
        call job_stop(s:review_job, 'kill')
        let s:review_job = v:null
    endif

    if s:review_bufnr != -1 && bufexists(s:review_bufnr)
        execute 'bwipeout ' . s:review_bufnr
    endif
endfunction

" Clean up when review buffer is closed
function! vim4rabbit#CleanupReview()
    " Cancel any running job
    if s:review_job != v:null && job_status(s:review_job) ==# 'run'
        call job_stop(s:review_job, 'kill')
    endif
    let s:review_job = v:null
    let s:review_bufnr = -1
endfunction
