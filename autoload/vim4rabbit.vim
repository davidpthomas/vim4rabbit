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

" Animation state
let s:spinner_timer = v:null
let s:spinner_frame = 0
let s:animation_frame_count = 24

" Elapsed time tracking
let s:review_start_time = []
let s:review_elapsed_secs = 0

" No-work animation state
let s:no_work_timer = v:null
let s:no_work_frame = 0
let s:no_work_frame_count = 8

" Game state
let s:game_timer = v:null
let s:game_active = 0
let s:game_mode = ''
let s:game_bufnr = -1
let s:matrix_match_ids = []

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

    " Calculate 20% of total window height (fixed at 6 lines for compact display)
    let l:height = float2nr(&lines * 0.2)
    if l:height < 6
        let l:height = 6
    endif
    if l:height > 6
        let l:height = 6
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
    nnoremap <buffer> <silent> u :call vim4rabbit#CloseHelp() \| call vim4rabbit#Review('uncommitted')<CR>
    nnoremap <buffer> <silent> c :call vim4rabbit#CloseHelp() \| call vim4rabbit#Review('committed')<CR>
    nnoremap <buffer> <silent> a :call vim4rabbit#CloseHelp() \| call vim4rabbit#Review('all')<CR>

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
    if l:height < 6
        let l:height = 6
    endif
    if l:height > 6
        let l:height = 6
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

    " Name the buffer with branch context (instead of default [Scratch])
    let l:branch = substitute(system('git rev-parse --abbrev-ref HEAD'), '\n', '', '')
    execute 'silent file ' . fnameescape('Rabbit Review (' . l:branch . ')')

    " Show loading message with cancel option
    let l:loading = py3eval('vim4rabbit.vim_get_loading_content()')
    setlocal modifiable
    call setline(1, l:loading)
    setlocal nomodifiable
    redraw

    " Map 'q' to close, 'c' to cancel, 'p' to play games
    nnoremap <buffer> <silent> q :call vim4rabbit#CloseReview()<CR>
    nnoremap <buffer> <silent> c :call vim4rabbit#CancelReview()<CR>
    nnoremap <buffer> <silent> p :call vim4rabbit#ShowGameMenu()<CR>

    " Fold navigation
    nnoremap <buffer> <silent> <CR> za
    nnoremap <buffer> <silent> zM zM
    nnoremap <buffer> <silent> zR zR

    " Selection
    nnoremap <buffer> <silent> <Space> :call vim4rabbit#ToggleIssueSelection()<CR>
    nnoremap <buffer> <silent> <leader>a :call vim4rabbit#SelectAllIssues()<CR>
    nnoremap <buffer> <silent> <leader>n :call vim4rabbit#DeselectAllIssues()<CR>

    " Claude integration
    nnoremap <buffer> <silent> @ :call vim4rabbit#LaunchClaude()<CR>

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

    " Record start time for elapsed timer
    let s:review_start_time = reltime()
    let s:review_elapsed_secs = 0

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

    " Calculate elapsed seconds
    let l:elapsed_secs = float2nr(reltimefloat(reltime(s:review_start_time)))

    " Get current animation frame from Python with elapsed time
    let l:content = py3eval('vim4rabbit.vim_get_animation_frame(' . s:spinner_frame . ', ' . l:elapsed_secs . ')')
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
    " Capture elapsed time before stopping spinner
    let s:review_elapsed_secs = float2nr(reltimefloat(reltime(s:review_start_time)))

    " Stop the spinner (game keeps running if active)
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

    " Format output via Python (pass elapsed time for display)
    if a:exit_status != 0
        let l:review = py3eval("vim4rabbit.vim_format_review(False, [], " . json_encode(l:output) . ", " . s:review_elapsed_secs . ")")
    else
        let l:result = py3eval("vim4rabbit.vim_parse_review_output(" . json_encode(l:output) . ")")
        let l:review = py3eval('vim4rabbit.vim_format_review(' .
            \ l:result.success . ', ' .
            \ string(l:result.issues_data) . ', ' .
            \ string(l:result.error_message) . ', ' .
            \ s:review_elapsed_secs . ')')
        " Store issues data for Claude integration
        call s:StoreIssuesData(l:result.issues_data)
    endif

    " Update buffer content (unpack dict from Python)
    call s:UpdateReviewBuffer(l:review.lines, l:review.issue_count)
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
    " Stop the spinner and any active game
    call s:StopSpinner()
    call s:StopGame()

    " Close game buffer first
    if s:game_bufnr != -1 && bufexists(s:game_bufnr)
        execute 'bwipeout ' . s:game_bufnr
    endif

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
function! s:UpdateReviewBuffer(content, issue_count)
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

    " Initialize selection tracking in Python
    call py3eval('vim4rabbit.vim_init_selections(' . a:issue_count . ')')

    " Remap 'c' from cancel to close now that job is done
    nnoremap <buffer> <silent> c :call vim4rabbit#CloseReview()<CR>

    execute l:cur_winnr . 'wincmd w'
    redraw
endfunction

" Display an error in the review buffer
function! s:DisplayReviewError(message)
    let l:review = py3eval('vim4rabbit.vim_format_review(False, [], ' . string(a:message) . ')')
    call s:UpdateReviewBuffer(l:review.lines, l:review.issue_count)
endfunction

" Close the review buffer
function! vim4rabbit#CloseReview()
    " Stop the spinner
    call s:StopSpinner()

    " Stop any active game
    call s:StopGame()

    " Close game buffer first
    if s:game_bufnr != -1 && bufexists(s:game_bufnr)
        execute 'bwipeout ' . s:game_bufnr
    endif

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

    " Stop any active game
    call s:StopGame()

    " Close game buffer if it exists
    if s:game_bufnr != -1 && bufexists(s:game_bufnr)
        execute 'bwipeout ' . s:game_bufnr
    endif

    " Stop the no-work animation
    call s:StopNoWorkAnimation()

    " Cancel any running job
    if s:review_job != v:null && job_status(s:review_job) ==# 'run'
        call job_stop(s:review_job, 'kill')
    endif
    let s:review_job = v:null
    let s:review_bufnr = -1

    " Clear selection state in Python
    call py3eval('vim4rabbit.vim_reset_selections()')
endfunction

" Custom fold text for review issues - shows type and summary
function! vim4rabbit#FoldText()
    let l:line = getline(v:foldstart)
    " Remove the fold marker from display
    let l:line = substitute(l:line, '\s*{{{$', '', '')
    return l:line
endfunction

" Get the issue number at the current cursor position
function! vim4rabbit#GetIssueAtCursor()
    " Pass buffer lines and 0-based cursor index to Python
    let l:lines = getline(1, '$')
    let l:cursor_idx = line('.') - 1
    return py3eval('vim4rabbit.vim_find_issue_at_line(' . string(l:lines) . ', ' . l:cursor_idx . ')')
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

    " Toggle in Python, get new state
    let l:selected = py3eval('vim4rabbit.vim_toggle_selection(' . l:issue_num . ')')
    call vim4rabbit#UpdateCheckbox(l:issue_num, l:selected)
endfunction

" Select all issues
function! vim4rabbit#SelectAllIssues()
    let l:count = py3eval('vim4rabbit.vim_select_all()')
    if l:count == 0
        return
    endif

    for l:i in range(1, l:count)
        call vim4rabbit#UpdateCheckbox(l:i, 1)
    endfor

    echo "Selected all " . l:count . " issue(s)"
endfunction

" Deselect all issues
function! vim4rabbit#DeselectAllIssues()
    let l:count = py3eval('vim4rabbit.vim_get_issue_count()')
    if l:count == 0
        return
    endif

    call py3eval('vim4rabbit.vim_deselect_all()')

    for l:i in range(1, l:count)
        call vim4rabbit#UpdateCheckbox(l:i, 0)
    endfor

    echo "Deselected all issues"
endfunction

" Get list of selected issue numbers
function! vim4rabbit#GetSelectedIssues()
    return py3eval('vim4rabbit.vim_get_selected()')
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

    " Write prompt to a temp file to avoid OS argument length limits (ARG_MAX)
    let l:tmpfile = tempname()
    call writefile(split(l:prompt, "\n", 1), l:tmpfile)

    " Open terminal with Claude CLI in a vertical split
    let l:term_opts = {
        \ 'term_name': 'Claude Code',
        \ 'vertical': 1,
        \ 'term_finish': 'close',
        \ }

    " Start Claude without prompt argument; send via terminal input instead
    let l:buf = term_start(['claude'], l:term_opts)

    " Send prompt via terminal input after Claude initializes
    call timer_start(2000, function('s:SendPromptToTerminal', [l:buf, l:tmpfile]))
endfunction

" Send prompt content from temp file to a running terminal buffer
function! s:SendPromptToTerminal(buf, tmpfile, timer) abort
    try
        if bufexists(a:buf) && term_getstatus(a:buf) =~# 'running'
            let l:prompt = join(readfile(a:tmpfile), "\n")
            " Use bracketed paste mode so newlines are treated as literal
            " text rather than individual Enter keypresses
            call term_sendkeys(a:buf, "\e[200~" . l:prompt . "\e[201~\r")
        endif
    finally
        call delete(a:tmpfile)
    endtry
endfunction

" =========================================================================
" Game functions
" =========================================================================

" Create a new game buffer below the review buffer
function! s:CreateGameBuffer()
    " Focus the review buffer first so split goes below it
    let l:winnr = bufwinnr(s:review_bufnr)
    if l:winnr == -1
        return -1
    endif

    let l:cur_winnr = winnr()
    execute l:winnr . 'wincmd w'

    " Open a horizontal split below the review buffer
    belowright new

    let s:game_bufnr = bufnr('%')

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
    setlocal nolist

    " Increase game buffer height for better visibility
    execute 'resize +5'

    " Name the buffer
    execute 'silent file ' . fnameescape('Rabbit Game')

    " Clean up when buffer is wiped
    autocmd BufWipeout <buffer> call vim4rabbit#CleanupGameBuffer()

    return s:game_bufnr
endfunction

" Clean up when game buffer is closed
function! vim4rabbit#CleanupGameBuffer()
    let s:game_bufnr = -1
    call s:StopGame()

    " Restore 'p' keymap on review buffer
    if s:review_bufnr != -1 && bufexists(s:review_bufnr)
        let l:winnr = bufwinnr(s:review_bufnr)
        if l:winnr != -1
            let l:cur_winnr = winnr()
            execute l:winnr . 'wincmd w'
            nnoremap <buffer> <silent> p :call vim4rabbit#ShowGameMenu()<CR>
            execute l:cur_winnr . 'wincmd w'
        endif
    endif
endfunction

" Show the game selection menu
function! vim4rabbit#ShowGameMenu()
    if s:review_bufnr == -1 || !bufexists(s:review_bufnr)
        return
    endif

    " Don't stop the spinner — it keeps running in the review buffer

    let s:game_mode = 'menu'

    " Create game buffer (opens split below review)
    let l:bufnr = s:CreateGameBuffer()
    if l:bufnr == -1
        return
    endif

    " Get menu content from Python (centered to game buffer dimensions)
    let l:width = winwidth(0)
    let l:height = winheight(0)
    let l:content = py3eval('vim4rabbit.vim_get_game_menu(' . l:width . ', ' . l:height . ')')

    " Write menu content into game buffer (we're already in it after CreateGameBuffer)
    setlocal modifiable
    call setline(1, l:content)
    setlocal nomodifiable

    " Set up menu keymaps on game buffer
    nnoremap <buffer> <silent> z :call vim4rabbit#StartGame('z')<CR>
    nnoremap <buffer> <silent> b :call vim4rabbit#StartGame('b')<CR>
    nnoremap <buffer> <silent> s :call vim4rabbit#StartGame('s')<CR>
    nnoremap <buffer> <silent> p :call vim4rabbit#StartGame('p')<CR>
    nnoremap <buffer> <silent> w :call vim4rabbit#StartGame('w')<CR>
    nnoremap <buffer> <silent> m :call vim4rabbit#StartGame('m')<CR>
    nnoremap <buffer> <silent> c :call vim4rabbit#CancelGame()<CR>

    " Remove 'p' from review buffer while game buffer is open
    let l:review_winnr = bufwinnr(s:review_bufnr)
    if l:review_winnr != -1
        let l:cur_winnr = winnr()
        execute l:review_winnr . 'wincmd w'
        silent! nunmap <buffer> p
        execute l:cur_winnr . 'wincmd w'
    endif

    redraw
endfunction

" Start a game
function! vim4rabbit#StartGame(key)
    if s:game_bufnr == -1 || !bufexists(s:game_bufnr)
        return
    endif

    let l:winnr = bufwinnr(s:game_bufnr)
    if l:winnr == -1
        return
    endif

    " Get game buffer dimensions
    let l:cur_winnr = winnr()
    execute l:winnr . 'wincmd w'
    let l:width = winwidth(0)
    let l:height = winheight(0)

    " Start game in Python, get tick rate
    let l:tick_rate = py3eval('vim4rabbit.vim_start_game("' . a:key . '", ' . l:width . ', ' . l:height . ')')
    if l:tick_rate == 0
        execute l:cur_winnr . 'wincmd w'
        return
    endif

    let s:game_active = 1
    let s:game_mode = a:key

    " Clear menu keymaps
    silent! nunmap <buffer> z
    silent! nunmap <buffer> b
    silent! nunmap <buffer> s
    silent! nunmap <buffer> p
    silent! nunmap <buffer> w
    silent! nunmap <buffer> m

    " Set up game keymaps — 'c' means cancel/go-back
    nnoremap <buffer> <silent> c :call vim4rabbit#CancelGame()<CR>

    " Rabbit-specific keymaps (h/j/k/l and w/a/s/d)
    if a:key ==# 's'
        nnoremap <buffer> <silent> h :call vim4rabbit#GameInput('h')<CR>
        nnoremap <buffer> <silent> j :call vim4rabbit#GameInput('j')<CR>
        nnoremap <buffer> <silent> k :call vim4rabbit#GameInput('k')<CR>
        nnoremap <buffer> <silent> l :call vim4rabbit#GameInput('l')<CR>
        nnoremap <buffer> <silent> a :call vim4rabbit#GameInput('a')<CR>
        nnoremap <buffer> <silent> s :call vim4rabbit#GameInput('s')<CR>
        nnoremap <buffer> <silent> d :call vim4rabbit#GameInput('d')<CR>
        nnoremap <buffer> <silent> w :call vim4rabbit#GameInput('w')<CR>
        nnoremap <buffer> <silent> p :call vim4rabbit#GameInput('p')<CR>
    endif

    " Pong-specific keymaps (j/k for paddle)
    if a:key ==# 'p'
        nnoremap <buffer> <silent> j :call vim4rabbit#GameInput('j')<CR>
        nnoremap <buffer> <silent> k :call vim4rabbit#GameInput('k')<CR>
    endif

    " WarGames keymaps (password letters + x to launch)
    if a:key ==# 'w'
        nnoremap <buffer> <silent> j :call vim4rabbit#GameInput('j')<CR>
        nnoremap <buffer> <silent> o :call vim4rabbit#GameInput('o')<CR>
        nnoremap <buffer> <silent> s :call vim4rabbit#GameInput('s')<CR>
        nnoremap <buffer> <silent> h :call vim4rabbit#GameInput('h')<CR>
        nnoremap <buffer> <silent> u :call vim4rabbit#GameInput('u')<CR>
        nnoremap <buffer> <silent> a :call vim4rabbit#GameInput('a')<CR>
        nnoremap <buffer> <silent> x :call vim4rabbit#GameInput('x')<CR>
    endif

    " Matrix-specific highlighting and char set toggle
    if a:key ==# 'm'
        highlight MatrixBg    guifg=#003B00 guibg=#0D0208 ctermfg=22  ctermbg=0
        highlight MatrixTrail guifg=#003B00 guibg=#0D0208 ctermfg=22  ctermbg=0
        highlight MatrixBody  guifg=#008F11 guibg=#0D0208 ctermfg=28  ctermbg=0
        highlight MatrixHead  guifg=#00FF41 guibg=#0D0208 ctermfg=46  ctermbg=0
        highlight MatrixWhite guifg=#FFFFFF guibg=#0D0208 ctermfg=15  ctermbg=0 gui=bold cterm=bold
        setlocal nowrap
        if exists('+wincolor')
            setlocal wincolor=MatrixBg
        endif
        call s:ApplyMatrixPatterns()
        nnoremap <buffer> <silent> n :call vim4rabbit#GameInput('n')<CR>
        nnoremap <buffer> <silent> s :call vim4rabbit#GameInput('s')<CR>
        nnoremap <buffer> <silent> r :call vim4rabbit#GameInput('r')<CR>
    endif

    " Render first frame
    let l:content = py3eval('vim4rabbit.vim_tick_game()')
    setlocal modifiable
    silent! %delete _
    call setline(1, l:content)
    setlocal nomodifiable

    execute l:cur_winnr . 'wincmd w'

    " Start game timer
    let s:game_timer = timer_start(l:tick_rate, function('s:UpdateGame'), {'repeat': -1})
    redraw
endfunction

" Apply/reapply matrix highlight match patterns from Python
function! s:ApplyMatrixPatterns()
    for l:id in s:matrix_match_ids
        silent! call matchdelete(l:id)
    endfor
    let s:matrix_match_ids = []
    let l:patterns = py3eval('vim4rabbit.vim_get_game_match_patterns()')
    for l:pair in l:patterns
        let l:id = matchadd(l:pair[0], l:pair[1])
        call add(s:matrix_match_ids, l:id)
    endfor
    " Status bar in white (priority 11 beats default 10)
    let l:id = matchadd('MatrixWhite', '.*Enter the Matrix.*', 11)
    call add(s:matrix_match_ids, l:id)
endfunction

" Timer callback for game updates
function! s:UpdateGame(timer)
    if s:game_bufnr == -1 || !bufexists(s:game_bufnr)
        call s:StopGame()
        return
    endif

    let l:winnr = bufwinnr(s:game_bufnr)
    if l:winnr == -1
        return
    endif

    let l:content = py3eval('vim4rabbit.vim_tick_game()')

    let l:cur_winnr = winnr()
    execute l:winnr . 'wincmd w'
    setlocal modifiable
    silent! %delete _
    call setline(1, l:content)
    setlocal nomodifiable
    execute l:cur_winnr . 'wincmd w'
    redraw
endfunction

" Handle game input (forward key to Python)
function! vim4rabbit#GameInput(key)
    if s:game_bufnr == -1 || !bufexists(s:game_bufnr)
        return
    endif

    let l:winnr = bufwinnr(s:game_bufnr)
    if l:winnr == -1
        return
    endif

    let l:content = py3eval('vim4rabbit.vim_input_game("' . a:key . '")')

    let l:cur_winnr = winnr()
    execute l:winnr . 'wincmd w'
    setlocal modifiable
    silent! %delete _
    call setline(1, l:content)
    setlocal nomodifiable

    " Re-apply matrix match patterns after char set change
    if s:game_mode ==# 'm' && (a:key ==# 'n' || a:key ==# 's' || a:key ==# 'r')
        call s:ApplyMatrixPatterns()
    endif

    execute l:cur_winnr . 'wincmd w'
    redraw
endfunction

" Cancel game and close game buffer (return to loading)
function! vim4rabbit#CancelGame()
    call s:StopGame()

    " Close the game buffer — BufWipeout autocmd will restore 'p' keymap
    if s:game_bufnr != -1 && bufexists(s:game_bufnr)
        execute 'bwipeout ' . s:game_bufnr
    endif

    " Focus the review buffer
    if s:review_bufnr != -1 && bufexists(s:review_bufnr)
        let l:winnr = bufwinnr(s:review_bufnr)
        if l:winnr != -1
            execute l:winnr . 'wincmd w'
        endif
    endif
endfunction

" Stop game timer and clear state
function! s:StopGame()
    if s:game_timer != v:null
        call timer_stop(s:game_timer)
        let s:game_timer = v:null
    endif
    let s:game_active = 0
    let s:game_mode = ''
    py3 vim4rabbit.vim_stop_game()
endfunction
