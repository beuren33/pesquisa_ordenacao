section .text
global bubble_sort

bubble_sort:
    push rbp
    mov rbp, rsp

    cmp rsi, 2
    jl .done

    mov rcx, rsi
    dec rcx

.outer:
    cmp rcx, 0
    je .done

    xor r8, r8
    xor r9, r9

.inner:
    cmp r8, rcx
    jge .inner_done

    mov eax, [rdi + r8*4]
    mov edx, [rdi + r8*4 + 4]
    cmp eax, edx
    jle .no_swap

    mov [rdi + r8*4], edx
    mov [rdi + r8*4 + 4], eax
    mov r9, 1

.no_swap:
    inc r8
    jmp .inner

.inner_done:
    cmp r9, 0
    je .done
    dec rcx
    jmp .outer

.done:
    pop rbp
    ret
