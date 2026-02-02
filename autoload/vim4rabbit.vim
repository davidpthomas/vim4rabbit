" vim4rabbit autoload functions
" These functions are loaded on-demand when called

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
" Expected format: {"used": 12345, "limit": 100000, "provider": "coderabbit"}
function! vim4rabbit#LoadTokenUsage()
    let l:file = expand('~/.vim4rabbit/usage.json')
    if filereadable(l:file)
        try
            let l:content = join(readfile(l:file), '')
            let l:data = json_decode(l:content)
            if type(l:data) == v:t_dict
                let g:vim4rabbit_tokens.used = get(l:data, 'used', 0)
                let g:vim4rabbit_tokens.limit = get(l:data, 'limit', 0)
                let g:vim4rabbit_tokens.provider = get(l:data, 'provider', 'rabbit')
            endif
        catch
            " Silently ignore parse errors
        endtry
    endif
    redrawstatus
endfunction

" Set token usage directly (call from API response handlers)
function! vim4rabbit#SetTokenUsage(used, limit, ...)
    let g:vim4rabbit_tokens.used = a:used
    let g:vim4rabbit_tokens.limit = a:limit
    if a:0 > 0
        let g:vim4rabbit_tokens.provider = a:1
    endif
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

        " Fetch and update token usage after successful review
        call vim4rabbit#FetchTokenUsage()
    endif

    " Add token usage to review output if available
    if g:vim4rabbit_tokens.limit > 0
        let l:pct = (g:vim4rabbit_tokens.used * 100) / g:vim4rabbit_tokens.limit
        call add(l:content, '')
        call add(l:content, '  ────────────────────────────────────────')
        call add(l:content, printf('  Token usage: %d / %d (%d%%)',
            \ g:vim4rabbit_tokens.used,
            \ g:vim4rabbit_tokens.limit,
            \ l:pct))
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

" Fetch token usage from CodeRabbit CLI
" Tries multiple methods: 'coderabbit usage', config file, or cache
function! vim4rabbit#FetchTokenUsage()
    " Method 1: Try 'coderabbit usage --json' command
    let l:usage_output = system('coderabbit usage --json 2>/dev/null')
    if v:shell_error == 0 && l:usage_output !~# '^\s*$'
        call vim4rabbit#ParseUsageJson(l:usage_output)
        return
    endif

    " Method 2: Try 'coderabbit usage' plain text
    let l:usage_output = system('coderabbit usage 2>/dev/null')
    if v:shell_error == 0 && l:usage_output !~# '^\s*$'
        call vim4rabbit#ParseUsagePlain(l:usage_output)
        return
    endif

    " Method 3: Check CodeRabbit config directory for usage file
    let l:cr_usage_file = expand('~/.config/coderabbit/usage.json')
    if filereadable(l:cr_usage_file)
        try
            let l:content = join(readfile(l:cr_usage_file), '')
            call vim4rabbit#ParseUsageJson(l:content)
            return
        catch
        endtry
    endif

    " Method 4: Fall back to our cache file
    call vim4rabbit#LoadTokenUsage()
endfunction

" Parse JSON usage output from CodeRabbit
" Expected formats:
"   {"used": 12345, "limit": 100000}
"   {"usage": {"tokens_used": 12345, "tokens_limit": 100000}}
"   {"plan": {"usage": 12345, "limit": 100000}}
function! vim4rabbit#ParseUsageJson(json_str)
    try
        let l:data = json_decode(a:json_str)
        if type(l:data) != v:t_dict
            return
        endif

        let l:used = 0
        let l:limit = 0

        " Try different JSON structures
        if has_key(l:data, 'used') && has_key(l:data, 'limit')
            let l:used = l:data.used
            let l:limit = l:data.limit
        elseif has_key(l:data, 'usage') && type(l:data.usage) == v:t_dict
            let l:used = get(l:data.usage, 'tokens_used', get(l:data.usage, 'used', 0))
            let l:limit = get(l:data.usage, 'tokens_limit', get(l:data.usage, 'limit', 0))
        elseif has_key(l:data, 'plan') && type(l:data.plan) == v:t_dict
            let l:used = get(l:data.plan, 'usage', get(l:data.plan, 'used', 0))
            let l:limit = get(l:data.plan, 'limit', 0)
        elseif has_key(l:data, 'tokens_used') && has_key(l:data, 'tokens_limit')
            let l:used = l:data.tokens_used
            let l:limit = l:data.tokens_limit
        endif

        if l:limit > 0
            call vim4rabbit#SetTokenUsage(l:used, l:limit, 'coderabbit')
            call vim4rabbit#SaveTokenCache()
        endif
    catch
        " JSON parse failed, ignore
    endtry
endfunction

" Parse plain text usage output from CodeRabbit
" Looks for patterns like:
"   "Used: 12,345 / 100,000 tokens"
"   "Usage: 45%"
"   "12345/100000"
function! vim4rabbit#ParseUsagePlain(text)
    let l:used = 0
    let l:limit = 0

    " Pattern: "Used: 12,345 / 100,000" or "12345 / 100000"
    let l:match = matchlist(a:text, '\(\d[0-9,]*\)\s*/\s*\(\d[0-9,]*\)')
    if !empty(l:match)
        let l:used = str2nr(substitute(l:match[1], ',', '', 'g'))
        let l:limit = str2nr(substitute(l:match[2], ',', '', 'g'))
    endif

    " Pattern: "tokens_used: 12345" and "tokens_limit: 100000"
    if l:limit == 0
        let l:used_match = matchlist(a:text, 'tokens\?[_\s]*used[:\s]\+\(\d[0-9,]*\)')
        let l:limit_match = matchlist(a:text, 'tokens\?[_\s]*limit[:\s]\+\(\d[0-9,]*\)')
        if !empty(l:used_match) && !empty(l:limit_match)
            let l:used = str2nr(substitute(l:used_match[1], ',', '', 'g'))
            let l:limit = str2nr(substitute(l:limit_match[1], ',', '', 'g'))
        endif
    endif

    if l:limit > 0
        call vim4rabbit#SetTokenUsage(l:used, l:limit, 'coderabbit')
        call vim4rabbit#SaveTokenCache()
    endif
endfunction

" Save token usage to cache file for persistence
function! vim4rabbit#SaveTokenCache()
    let l:dir = expand('~/.vim4rabbit')
    if !isdirectory(l:dir)
        call mkdir(l:dir, 'p')
    endif

    let l:file = l:dir . '/usage.json'
    let l:data = json_encode(g:vim4rabbit_tokens)
    call writefile([l:data], l:file)
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
