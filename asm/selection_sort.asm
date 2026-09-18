section .text
global selection_sort

selection_sort:
    push rbp
    mov rbp, rsp

    cmp rsi, 2
    jl .done

    xor rcx, rcx

.outer:
    mov rax, rsi
    dec rax
    cmp rcx, rax
    jge .done

    mov r8, rcx
    mov r9, rcx
    inc r9

.inner:
    cmp r9, rsi
    jge .after_inner

    mov edx, [rdi + r9*4]
    mov eax, [rdi + r8*4]
    cmp edx, eax
    jge .no_update
    mov r8, r9

.no_update:
    inc r9
    jmp .inner

.after_inner:
    cmp r8, rcx
    je .no_swap
    mov eax, [rdi + rcx*4]
    mov edx, [rdi + r8*4]
    mov [rdi + rcx*4], edx
    mov [rdi + r8*4], eax

.no_swap:
    inc rcx
    jmp .outer

.done:
    pop rbp
    ret
