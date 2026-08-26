; selection_sort.asm
; void selection_sort(int32_t *arr, int64_t n)
; System V AMD64 ABI: rdi = arr, rsi = n

section .text
global selection_sort

selection_sort:
    push rbp
    mov rbp, rsp

    cmp rsi, 2
    jl .done                   ; n < 2 -> nada a fazer

    xor rcx, rcx                ; i = 0

.outer:
    mov rax, rsi
    dec rax                     ; n - 1
    cmp rcx, rax
    jge .done                   ; i >= n-1 -> done

    mov r8, rcx                 ; min_idx = i
    mov r9, rcx
    inc r9                      ; j = i + 1

.inner:
    cmp r9, rsi
    jge .after_inner

    mov edx, [rdi + r9*4]       ; arr[j]
    mov eax, [rdi + r8*4]       ; arr[min_idx]
    cmp edx, eax
    jge .no_update
    mov r8, r9                  ; min_idx = j

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
