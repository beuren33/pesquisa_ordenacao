section .text
global quick_sort

quick_sort:
    cmp rsi, 2
    jl .done

    push rbp
    mov rbp, rsp

    mov rdx, rsi
    dec rdx
    xor rsi, rsi
    call .qsort_rec

    pop rbp
.done:
    ret

.qsort_rec:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14

    mov rbx, rdi
    mov r12, rsi
    mov r13, rdx

.qs_loop:
    cmp r12, r13
    jge .rec_done

    mov rdi, rbx
    mov rsi, r12
    mov rdx, r13
    call .partition
    mov r14, rax

    mov rax, r14
    sub rax, r12
    mov rcx, r13
    sub rcx, r14
    cmp rax, rcx
    jl .left_smaller

    mov rdi, rbx
    lea rsi, [r14 + 1]
    mov rdx, r13
    call .qsort_rec
    mov r13, r14
    dec r13
    jmp .qs_loop

.left_smaller:

    mov rdi, rbx
    mov rsi, r12
    lea rdx, [r14 - 1]
    call .qsort_rec
    mov r12, r14
    inc r12
    jmp .qs_loop

.rec_done:
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

.partition:
    mov r8, rdx
    sub r8, rsi
    sar r8, 1
    add r8, rsi

    mov eax, [rdi + rsi*4]
    mov ecx, [rdi + r8*4]
    mov r9d, [rdi + rdx*4]

    cmp eax, ecx
    jle .med_lo_le_mid

    xchg eax, ecx
.med_lo_le_mid:
    cmp ecx, r9d
    jle .med_mid_le_hi

    mov ecx, r9d
    cmp eax, ecx
    jle .med_mid_le_hi
    mov ecx, eax
.med_mid_le_hi:

    mov r9d, [rdi + rdx*4]
    cmp r9d, ecx
    je .med_done

    mov eax, [rdi + rsi*4]
    cmp eax, ecx
    jne .med_check_mid
    mov [rdi + rsi*4], r9d
    mov [rdi + rdx*4], ecx
    jmp .med_done
.med_check_mid:
    mov [rdi + r8*4], r9d
    mov [rdi + rdx*4], ecx
.med_done:
    mov r9d, ecx
    mov r10, rsi
    dec r10
    mov r11, rsi

.part_loop:
    cmp r11, rdx
    jge .part_after
    mov eax, [rdi + r11*4]
    cmp eax, r9d
    jg .part_no_swap
    inc r10
    mov ecx, [rdi + r10*4]
    mov [rdi + r10*4], eax
    mov [rdi + r11*4], ecx

.part_no_swap:
    inc r11
    jmp .part_loop

.part_after:
    inc r10
    mov eax, [rdi + r10*4]
    mov ecx, [rdi + rdx*4]
    mov [rdi + r10*4], ecx
    mov [rdi + rdx*4], eax
    mov rax, r10
    ret
