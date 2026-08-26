; insertion_sort.asm
; void insertion_sort(int32_t *arr, int64_t n)
; System V AMD64 ABI: rdi = arr, rsi = n

section .text
global insertion_sort

insertion_sort:
    push rbp
    mov rbp, rsp

    cmp rsi, 2
    jl .done                   ; n < 2 -> nada a fazer

    mov rcx, 1                 ; i = 1

.outer:
    cmp rcx, rsi
    jge .done

    mov eax, [rdi + rcx*4]     ; key = arr[i]
    mov r8, rcx
    dec r8                     ; j = i-1

.inner:
    cmp r8, 0
    jl .insert

    mov edx, [rdi + r8*4]      ; arr[j]
    cmp edx, eax
    jle .insert

    lea r9, [r8 + 1]
    mov [rdi + r9*4], edx      ; arr[j+1] = arr[j]
    dec r8
    jmp .inner

.insert:
    lea r9, [r8 + 1]
    mov [rdi + r9*4], eax      ; arr[j+1] = key

    inc rcx
    jmp .outer

.done:
    pop rbp
    ret
