" vim4rabbit autoload functions
" These functions are loaded on-demand when called

" ==============================================================================
" Processing State Variables
" ==============================================================================
let s:is_processing = 0
let s:spinner_index = 0
let s:spinner_timer = -1
let s:processing_message = ''
let s:job_output = []

" Spinner style definitions
let s:spinner_styles = {
    \ 'block':   ['█','▓','▒','░','▒','▓'],
    \ 'braille': ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'],
    \ 'ascii':   ['|','/','-','\']
    \ }

" ==============================================================================
" Indicator Functions
" ==============================================================================

function! vim4rabbit#StartProcessing(message) abort
    let s:is_processing = 1
    let s:spinner_index = 0
    let s:processing_message = a:message
    let s:job_output = []

    echo '[vim4rabbit] ' . a:message

    if s:spinner_timer != -1
        call timer_stop(s:spinner_timer)
    endif
    let s:spinner_timer = timer_start(100, function('vim4rabbit#UpdateSpinner'), {'repeat': -1})
endfunction

function! vim4rabbit#StopProcessing(success, message) abort
    let s:is_processing = 0
    let s:processing_message = ''

    if s:spinner_timer != -1
        call timer_stop(s:spinner_timer)
        let s:spinner_timer = -1
    endif

    redrawstatus

    if a:success
        echohl None
        echo '[vim4rabbit] ' . a:message
    else
        echohl WarningMsg
        echo '[vim4rabbit] ' . a:message
        echohl None
    endif
endfunction

function! s:GetSpinnerChar() abort
    let l:style = get(g:, 'vim4rabbit_spinner_style', 'block')
    if !has_key(s:spinner_styles, l:style)
        let l:style = 'block'
    endif
    let l:chars = s:spinner_styles[l:style]
    return l:chars[s:spinner_index % len(l:chars)]
endfunction

function! vim4rabbit#UpdateSpinner(timer) abort
    if !s:is_processing
        return
    endif
    let s:spinner_index += 1
    redrawstatus
endfunction

function! vim4rabbit#GetStatusLine() abort
    if !s:is_processing
        return ''
    endif
    let l:spinner = s:GetSpinnerChar()
    let l:msg = s:processing_message
    if empty(l:msg)
        let l:msg = 'Processing...'
    endif
    return '[vim4rabbit: ' . l:spinner . ' ' . l:msg . ']'
endfunction

" ==============================================================================
" CodeRabbit Integration
" ==============================================================================

function! vim4rabbit#RunCodeRabbit() abort
    call vim4rabbit#StartProcessing('Running CodeRabbit review...')

    let s:job_output = []
    let l:cmd = ['coderabbit', '--plain']

    if has('nvim')
        let s:coderabbit_job = jobstart(l:cmd, {
            \ 'on_stdout': function('s:OnJobOutput'),
            \ 'on_stderr': function('s:OnJobOutput'),
            \ 'on_exit': function('s:OnJobExit')
            \ })
    else
        let s:coderabbit_job = job_start(l:cmd, {
            \ 'out_cb': function('s:OnJobOutputVim'),
            \ 'err_cb': function('s:OnJobOutputVim'),
            \ 'exit_cb': function('s:OnJobExitVim')
            \ })
    endif
endfunction

function! s:OnJobOutput(job_id, data, event) abort
    call extend(s:job_output, a:data)
endfunction

function! s:OnJobExit(job_id, exit_code, event) abort
    call vim4rabbit#StopProcessing(a:exit_code == 0, 'CodeRabbit review complete!')
    call s:OpenResultsBuffer()
endfunction

function! s:OnJobOutputVim(channel, msg) abort
    call add(s:job_output, a:msg)
endfunction

function! s:OnJobExitVim(job, exit_code) abort
    call vim4rabbit#StopProcessing(a:exit_code == 0, 'CodeRabbit review complete!')
    call s:OpenResultsBuffer()
endfunction

function! s:OpenResultsBuffer() abort
    " Open new split for results
    new
    setlocal buftype=nofile
    setlocal bufhidden=wipe
    setlocal noswapfile
    setlocal nobuflisted
    setlocal filetype=markdown

    " Add header and results
    call setline(1, '# CodeRabbit Review Results')
    call append(1, '═══════════════════════════════════════')
    call append(2, '')

    let l:line = 3
    for l:output in s:job_output
        if !empty(l:output)
            call append(l:line, l:output)
            let l:line += 1
        endif
    endfor

    if l:line == 3
        call append(3, '(No output from CodeRabbit)')
    endif

    setlocal nomodifiable
endfunction

" ==============================================================================
" Test Function
" ==============================================================================

function! vim4rabbit#TestIndicator() abort
    call vim4rabbit#StartProcessing('Testing indicator...')
    call timer_start(3000, function('s:TestComplete'))
endfunction

function! s:TestComplete(timer) abort
    call vim4rabbit#StopProcessing(1, 'Test complete!')
endfunction

" ==============================================================================
" Buffer Functions
" ==============================================================================

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
    call setline(1, 'Welcome to vim4rabbit - Your AI-powered code companion!')
    call append(1, '')
    call append(2, 'Commands:')
    call append(3, '  :CR      - Open this buffer')
    call append(4, '  :CRTest  - Test the spinner indicator')

    " Make buffer read-only
    setlocal nomodifiable
endfunction
