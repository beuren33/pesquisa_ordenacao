; shell_sort.asm
; void shell_sort(int32_t *arr, int64_t n)
; System V AMD64 ABI: rdi = arr, rsi = n
; Sequencia de gaps: n/2, n/4, ..., 1 (Shell classico)

section .text
global shell_sort

shell_sort:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15

    cmp rsi, 2
    jl .done                   ; n < 2 -> nada a fazer

    mov r15, rsi                ; r15 = n
    mov r14, r15
    shr r14, 1                  ; r14 = gap = n/2

.gap_loop:
    cmp r14, 0
    je .done

    mov r12, r14                ; r12 = i = gap

.outer:
    cmp r12, r15
    jge .next_gap

    mov eax, [rdi + r12*4]      ; eax = temp = arr[i]
    mov r13, r12
    sub r13, r14                 ; r13 = j = i - gap

.inner:
    cmp r13, 0
    jl .insert

    mov ebx, [rdi + r13*4]       ; arr[j]
    cmp ebx, eax
    jle .insert

    lea rcx, [r13 + r14]
    mov [rdi + rcx*4], ebx       ; arr[j+gap] = arr[j]
    sub r13, r14
    jmp .inner

.insert:
    lea rcx, [r13 + r14]
    mov [rdi + rcx*4], eax       ; arr[j+gap] = temp

    inc r12
    jmp .outer

.next_gap:
    shr r14, 1
    jmp .gap_loop

.done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret
