section .text
global insertion_sort

insertion_sort:
    push rbp
    mov rbp, rsp

    cmp rsi, 2
    jl .done

    mov rcx, 1

.outer:
    cmp rcx, rsi
    jge .done

    mov eax, [rdi + rcx*4]
    mov r8, rcx
    dec r8

.inner:
    cmp r8, 0
    jl .insert

    mov edx, [rdi + r8*4]
    cmp edx, eax
    jle .insert

    lea r9, [r8 + 1]
    mov [rdi + r9*4], edx
    dec r8
    jmp .inner

.insert:
    lea r9, [r8 + 1]
    mov [rdi + r9*4], eax

    inc rcx
    jmp .outer

.done:
    pop rbp
    ret
