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

" Store issue count for selection functions
let s:review_issue_count = 0

" Animation state
let s:spinner_timer = v:null
let s:spinner_frame = 0
let s:animation_frame_count = 24

" No-work animation state
let s:no_work_timer = v:null
let s:no_work_frame = 0
let s:no_work_frame_count = 8

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
        call vim4rabbit#Review('uncommitted')
    elseif l:cmd ==# 'review uncommitted'
        call vim4rabbit#Review('uncommitted')
    elseif l:cmd ==# 'review committed'
        call vim4rabbit#Review('committed')
    elseif l:cmd ==# 'review all'
        call vim4rabbit#Review('all')
    else
        echo "Unknown rabbit command: " . l:cmd
        echo "Available commands: help, review, review uncommitted, review committed, review all"
    endif
endfunction

" Command completion for :Rabbit
function! vim4rabbit#CompleteRabbit(ArgLead, CmdLine, CursorPos)
    let l:commands = ['help', 'review', 'review uncommitted', 'review committed', 'review all']
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
    nnoremap <buffer> <silent> ru :call vim4rabbit#CloseHelp() \| call vim4rabbit#Review('uncommitted')<CR>
    nnoremap <buffer> <silent> rc :call vim4rabbit#CloseHelp() \| call vim4rabbit#Review('committed')<CR>
    nnoremap <buffer> <silent> ra :call vim4rabbit#CloseHelp() \| call vim4rabbit#Review('all')<CR>

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
" Optional argument: review_type ('uncommitted' or 'committed', default 'uncommitted')
function! vim4rabbit#Review(...)
    " Get review type from argument, default to 'uncommitted'
    let l:review_type = a:0 > 0 ? a:1 : 'uncommitted'

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

    " Fold navigation
    nnoremap <buffer> <silent> <CR> za
    nnoremap <buffer> <silent> zM zM
    nnoremap <buffer> <silent> zR zR

    " Selection
    nnoremap <buffer> <silent> <Space> :call vim4rabbit#ToggleIssueSelection()<CR>
    nnoremap <buffer> <silent> <leader>a :call vim4rabbit#SelectAllIssues()<CR>
    nnoremap <buffer> <silent> <leader>n :call vim4rabbit#DeselectAllIssues()<CR>

    " Claude integration
    nnoremap <buffer> <silent> <leader>c :call vim4rabbit#LaunchClaude()<CR>

    " Clean up when buffer is wiped
    autocmd BufWipeout <buffer> call vim4rabbit#CleanupReview()

    " Run the review asynchronously
    call vim4rabbit#RunReviewAsync(l:review_type)
endfunction

" Run CodeRabbit CLI asynchronously
" Argument: review_type ('uncommitted' or 'committed')
function! vim4rabbit#RunReviewAsync(review_type)
    " Reset output collector
    let s:review_output = []

    " Start the animation
    let s:spinner_frame = 0
    call s:UpdateSpinner(0)
    let s:spinner_timer = timer_start(750, function('s:UpdateSpinner'), {'repeat': -1})

    " Build the command based on review type
    let l:cmd = ['coderabbit', 'review', '--type', a:review_type, '--plain']

    let s:review_job = job_start(l:cmd, {
        \ 'out_cb': function('s:OnReviewOutput'),
        \ 'err_cb': function('s:OnReviewOutput'),
        \ 'exit_cb': function('s:OnReviewExit'),
        \ 'mode': 'raw',
        \ })

    if job_status(s:review_job) ==# 'fail'
        call s:StopSpinner()
        call s:DisplayReviewError('Failed to start coderabbit')
    endif
endfunction

" Update the animation in the review buffer
function! s:UpdateSpinner(timer)
    if s:review_bufnr == -1 || !bufexists(s:review_bufnr)
        call s:StopSpinner()
        return
    endif

    let l:winnr = bufwinnr(s:review_bufnr)
    if l:winnr == -1
        return
    endif

    " Get current animation frame from Python
    let l:content = py3eval('vim4rabbit.vim_get_animation_frame(' . s:spinner_frame . ')')
    let s:spinner_frame = (s:spinner_frame + 1) % s:animation_frame_count

    " Update buffer
    let l:cur_winnr = winnr()
    execute l:winnr . 'wincmd w'
    setlocal modifiable
    silent! %delete _
    call setline(1, l:content)
    setlocal nomodifiable
    execute l:cur_winnr . 'wincmd w'
    redraw
endfunction

" Stop the spinner timer
function! s:StopSpinner()
    if s:spinner_timer != v:null
        call timer_stop(s:spinner_timer)
        let s:spinner_timer = v:null
    endif
endfunction

" Start the no-work animation
function! s:StartNoWorkAnimation()
    let s:no_work_frame = 0
    call s:UpdateNoWorkAnimation(0)
    let s:no_work_timer = timer_start(750, function('s:UpdateNoWorkAnimation'), {'repeat': -1})
endfunction

" Stop the no-work animation timer
function! s:StopNoWorkAnimation()
    if s:no_work_timer != v:null
        call timer_stop(s:no_work_timer)
        let s:no_work_timer = v:null
    endif
endfunction

" Update the no-work animation in the review buffer
function! s:UpdateNoWorkAnimation(timer)
    if s:review_bufnr == -1 || !bufexists(s:review_bufnr)
        call s:StopNoWorkAnimation()
        return
    endif

    let l:winnr = bufwinnr(s:review_bufnr)
    if l:winnr == -1
        return
    endif

    " Get current animation frame from Python
    let l:content = py3eval('vim4rabbit.vim_get_no_work_animation_frame(' . s:no_work_frame . ')')
    let s:no_work_frame = (s:no_work_frame + 1) % s:no_work_frame_count

    " Update buffer
    let l:cur_winnr = winnr()
    execute l:winnr . 'wincmd w'
    setlocal modifiable
    silent! %delete _
    call setline(1, l:content)
    setlocal nomodifiable
    execute l:cur_winnr . 'wincmd w'
    redraw
endfunction

" Callback for job output (stdout and stderr)
function! s:OnReviewOutput(channel, msg)
    call add(s:review_output, a:msg)
endfunction

" Callback when job exits
function! s:OnReviewExit(job, exit_status)
    " Stop the spinner
    call s:StopSpinner()

    " Clear the job reference
    let s:review_job = v:null

    " Check if buffer still exists
    if s:review_bufnr == -1 || !bufexists(s:review_bufnr)
        return
    endif

    " Combine output
    let l:output = join(s:review_output, '')

    " Check if this is a "no files" error - show jumping rabbit animation
    if a:exit_status != 0 && py3eval('vim4rabbit.vim_is_no_files_error(' . json_encode(l:output) . ')')
        call s:StartNoWorkAnimation()
        return
    endif

    " Format output via Python
    if a:exit_status != 0
        let l:content = py3eval("vim4rabbit.vim_format_review(False, [], " . json_encode(l:output) . ")")
    else
        let l:result = py3eval("vim4rabbit.vim_parse_review_output(" . json_encode(l:output) . ")")
        let l:content = py3eval('vim4rabbit.vim_format_review(' .
            \ l:result.success . ', ' .
            \ string(l:result.issues) . ', ' .
            \ string(l:result.error_message) . ')')
        " Store issues data for Claude integration
        call s:StoreIssuesData(l:result.issues_data)
    endif

    " Update buffer content
    call s:UpdateReviewBuffer(l:content)
endfunction

" Store issues data in buffer-local variable for Claude integration
function! s:StoreIssuesData(issues_data)
    if s:review_bufnr == -1 || !bufexists(s:review_bufnr)
        return
    endif

    let l:winnr = bufwinnr(s:review_bufnr)
    if l:winnr == -1
        return
    endif

    let l:cur_winnr = winnr()
    execute l:winnr . 'wincmd w'
    let b:vim4rabbit_issues = a:issues_data
    execute l:cur_winnr . 'wincmd w'
endfunction

" Cancel the running review and close buffer
function! vim4rabbit#CancelReview()
    " Stop the spinner
    call s:StopSpinner()

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

    " Set up folding for review results
    setlocal foldmethod=marker
    setlocal foldmarker={{{,}}}
    setlocal foldlevel=0
    setlocal foldtext=vim4rabbit#FoldText()
    setlocal foldenable

    " Initialize selection tracking
    let b:vim4rabbit_selections = {}

    " Count issues for selection functions
    let s:review_issue_count = 0
    for l:line in a:content
        if l:line =~# '^\s*\[ \] \d\+\.'
            let s:review_issue_count += 1
        endif
    endfor

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
    " Stop the spinner
    call s:StopSpinner()

    " Stop the no-work animation
    call s:StopNoWorkAnimation()

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
    " Stop the spinner
    call s:StopSpinner()

    " Stop the no-work animation
    call s:StopNoWorkAnimation()

    " Cancel any running job
    if s:review_job != v:null && job_status(s:review_job) ==# 'run'
        call job_stop(s:review_job, 'kill')
    endif
    let s:review_job = v:null
    let s:review_bufnr = -1
    let s:review_issue_count = 0
endfunction

" Custom fold text for review issues
function! vim4rabbit#FoldText()
    let l:line = getline(v:foldstart)
    let l:numlines = v:foldend - v:foldstart + 1
    " Remove the fold marker from display
    let l:line = substitute(l:line, '\s*{{{$', '', '')
    return l:line . ' (' . l:numlines . ' lines)'
endfunction

" Get the issue number at the current cursor position
function! vim4rabbit#GetIssueAtCursor()
    let l:lnum = line('.')
    let l:line = getline(l:lnum)

    " Check if we're on a fold header line (has checkbox pattern)
    let l:match = matchlist(l:line, '^\s*\[\(.\)\]\s*\(\d\+\)\.')
    if !empty(l:match)
        return str2nr(l:match[2])
    endif

    " Check if we're inside a fold - look upward for the fold header
    let l:search_line = l:lnum
    while l:search_line > 0
        let l:search_text = getline(l:search_line)
        let l:match = matchlist(l:search_text, '^\s*\[\(.\)\]\s*\(\d\+\)\.')
        if !empty(l:match)
            return str2nr(l:match[2])
        endif
        " Stop if we hit a fold end marker (we went too far)
        if l:search_text =~# '}}}'
            break
        endif
        let l:search_line -= 1
    endwhile

    return 0
endfunction

" Find the line number of a specific issue's checkbox
function! s:FindIssueLine(issue_num)
    let l:pattern = '^\s*\[.\]\s*' . a:issue_num . '\.'
    let l:lnum = 1
    while l:lnum <= line('$')
        if getline(l:lnum) =~# l:pattern
            return l:lnum
        endif
        let l:lnum += 1
    endwhile
    return 0
endfunction

" Update the checkbox display for an issue
function! vim4rabbit#UpdateCheckbox(issue_num, selected)
    let l:lnum = s:FindIssueLine(a:issue_num)
    if l:lnum == 0
        return
    endif

    let l:line = getline(l:lnum)
    let l:new_char = a:selected ? 'x' : ' '
    let l:new_line = substitute(l:line, '^\(\s*\)\[.\]', '\1[' . l:new_char . ']', '')

    setlocal modifiable
    call setline(l:lnum, l:new_line)
    setlocal nomodifiable
endfunction

" Toggle issue selection at cursor
function! vim4rabbit#ToggleIssueSelection()
    let l:issue_num = vim4rabbit#GetIssueAtCursor()
    if l:issue_num == 0
        echo "No issue at cursor"
        return
    endif

    " Initialize selections dict if needed
    if !exists('b:vim4rabbit_selections')
        let b:vim4rabbit_selections = {}
    endif

    " Toggle selection state
    let l:key = string(l:issue_num)
    if has_key(b:vim4rabbit_selections, l:key) && b:vim4rabbit_selections[l:key]
        let b:vim4rabbit_selections[l:key] = 0
        call vim4rabbit#UpdateCheckbox(l:issue_num, 0)
    else
        let b:vim4rabbit_selections[l:key] = 1
        call vim4rabbit#UpdateCheckbox(l:issue_num, 1)
    endif
endfunction

" Select all issues
function! vim4rabbit#SelectAllIssues()
    if s:review_issue_count == 0
        return
    endif

    if !exists('b:vim4rabbit_selections')
        let b:vim4rabbit_selections = {}
    endif

    for l:i in range(1, s:review_issue_count)
        let b:vim4rabbit_selections[string(l:i)] = 1
        call vim4rabbit#UpdateCheckbox(l:i, 1)
    endfor

    echo "Selected all " . s:review_issue_count . " issue(s)"
endfunction

" Deselect all issues
function! vim4rabbit#DeselectAllIssues()
    if s:review_issue_count == 0
        return
    endif

    if !exists('b:vim4rabbit_selections')
        let b:vim4rabbit_selections = {}
    endif

    for l:i in range(1, s:review_issue_count)
        let b:vim4rabbit_selections[string(l:i)] = 0
        call vim4rabbit#UpdateCheckbox(l:i, 0)
    endfor

    echo "Deselected all issues"
endfunction

" Get list of selected issue numbers (placeholder for future AI integration)
function! vim4rabbit#GetSelectedIssues()
    if !exists('b:vim4rabbit_selections')
        return []
    endif

    let l:selected = []
    for [l:key, l:val] in items(b:vim4rabbit_selections)
        if l:val
            call add(l:selected, str2nr(l:key))
        endif
    endfor

    return sort(l:selected, 'n')
endfunction

" Placeholder for future AI-powered fix application
function! vim4rabbit#ApplySelectedFixes()
    let l:selected = vim4rabbit#GetSelectedIssues()
    if empty(l:selected)
        echo "No issues selected"
        return
    endif

    echo "Selected issues: " . join(l:selected, ', ') . " (AI fix not yet implemented)"
endfunction

" Launch Claude Code CLI with selected issues
function! vim4rabbit#LaunchClaude()
    let l:selected = vim4rabbit#GetSelectedIssues()
    if empty(l:selected)
        echo "No issues selected. Use Space to select issues."
        return
    endif

    " Check if issues data is available
    if !exists('b:vim4rabbit_issues') || empty(b:vim4rabbit_issues)
        echo "No issue data available. Please run a review first."
        return
    endif

    " Build the prompt via Python
    let l:prompt = py3eval('vim4rabbit.vim_build_claude_prompt(' .
        \ string(l:selected) . ', ' .
        \ json_encode(b:vim4rabbit_issues) . ')')

    if empty(l:prompt)
        echo "Could not build prompt for selected issues."
        return
    endif

    " Open terminal with Claude CLI in a vertical split
    " Use term_start for better control
    let l:term_opts = {
        \ 'term_name': 'Claude Code',
        \ 'vertical': 1,
        \ 'term_finish': 'close',
        \ }

    " Start the terminal with claude command and prompt
    call term_start(['claude', l:prompt], l:term_opts)
endfunction
