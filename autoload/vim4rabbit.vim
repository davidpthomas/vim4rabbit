" vim4rabbit autoload functions
" These functions are loaded on-demand when called

" Store buffer numbers for reference
let s:help_bufnr = -1
let s:review_bufnr = -1

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
    elseif a:subcmd ==# 'review'
        call vim4rabbit#Review()
    else
        echo "Unknown rabbit command: " . a:subcmd
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

    " Show loading message
    setlocal modifiable
    call setline(1, ['  🐰 coderabbit', '', '  Running coderabbit...'])
    setlocal nomodifiable
    redraw

    " Map 'q' to close the review buffer
    nnoremap <buffer> <silent> q :call vim4rabbit#CloseReview()<CR>

    " Clean up when buffer is wiped
    autocmd BufWipeout <buffer> call vim4rabbit#CleanupReview()

    " Run the review asynchronously
    call vim4rabbit#RunReview()
endfunction

" Run CodeRabbit CLI and display results
function! vim4rabbit#RunReview()
    " Run coderabbit CLI
    let l:output = system('coderabbit --plain 2>&1')
    let l:exit_code = v:shell_error

    " Parse the output and create summary
    let l:content = ['  🐰 coderabbit', '']

    if l:exit_code != 0
        call add(l:content, '  ⚠️  Error running coderabbit:')
        call add(l:content, '')
        for l:line in split(l:output, "\n")
            call add(l:content, '    ' . l:line)
        endfor
    else
        " Parse issues separated by equal signs (====+)
        let l:issues = vim4rabbit#ParseReviewIssues(l:output)

        if empty(l:issues)
            call add(l:content, '  ✓ No issues found!')
        else
            call add(l:content, '  Found ' . len(l:issues) . ' issue(s):')

            let l:issue_num = 1
            for l:issue in l:issues
                call add(l:content, '')
                call add(l:content, '  ════════════════════════════════════════')
                call add(l:content, '  Issue #' . l:issue_num)
                call add(l:content, '  ────────────────────────────────────────')
                for l:line in l:issue
                    call add(l:content, '    ' . l:line)
                endfor
                let l:issue_num += 1
            endfor
        endif
    endif

    call add(l:content, '')
    call add(l:content, '  Press [q] to close')

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

" Parse review output into separate issues
" Issues are separated by lines containing multiple equal signs (=====)
function! vim4rabbit#ParseReviewIssues(output)
    let l:issues = []
    let l:current_issue = []
    let l:in_issue = 0

    for l:line in split(a:output, "\n")
        " Check if this is a separator line (5+ equal signs)
        if l:line =~# '^=\{5,\}\s*$'
            " If we were collecting an issue, save it
            if l:in_issue && !empty(l:current_issue)
                call add(l:issues, l:current_issue)
            endif
            " Start a new issue
            let l:current_issue = []
            let l:in_issue = 1
        elseif l:in_issue
            " Add line to current issue (trim trailing whitespace)
            call add(l:current_issue, substitute(l:line, '\s\+$', '', ''))
        else
            " Content before first separator - could be header/summary
            " Start collecting as first issue if non-empty
            if l:line !~# '^\s*$'
                let l:in_issue = 1
                call add(l:current_issue, substitute(l:line, '\s\+$', '', ''))
            endif
        endif
    endfor

    " Don't forget the last issue
    if !empty(l:current_issue)
        call add(l:issues, l:current_issue)
    endif

    return l:issues
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
