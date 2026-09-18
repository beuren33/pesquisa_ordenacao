extern malloc
extern free

section .text
global merge_sort

merge_sort:
    cmp rsi, 2
    jl .done

    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    sub rsp, 8

    mov rbx, rdi
    mov r12, rsi

    mov rdi, r12
    shl rdi, 2
    call malloc wrt ..plt
    mov r13, rax

    mov rdi, rbx
    mov rsi, r13
    xor rdx, rdx
    mov rcx, r12
    dec rcx
    call .ms_rec

    mov rdi, r13
    call free wrt ..plt

    add rsp, 8
    pop r13
    pop r12
    pop rbx
    pop rbp
.done:
    ret

.ms_rec:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15

    mov rbx, rdi
    mov r12, rsi
    mov r13, rdx
    mov r14, rcx

    cmp r13, r14
    jge .ms_done

    mov rax, r14
    sub rax, r13
    sar rax, 1
    add rax, r13
    mov r15, rax

    mov rdi, rbx
    mov rsi, r12
    mov rdx, r13
    mov rcx, r15
    call .ms_rec

    mov rdi, rbx
    mov rsi, r12
    lea rdx, [r15 + 1]
    mov rcx, r14
    call .ms_rec

    mov rdi, rbx
    mov rsi, r12
    mov rdx, r13
    mov rcx, r15
    mov r8, r14
    call .ms_merge

.ms_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

.ms_merge:
    mov r9, rdx
    mov r10, rcx
    inc r10
    mov r11, rdx

.merge_loop:
    cmp r9, rcx
    jg .merge_left_done
    cmp r10, r8
    jg .merge_left_done
    mov eax, [rdi + r9*4]
    mov ebx, [rdi + r10*4]
    cmp eax, ebx
    jg .merge_take_right
    mov [rsi + r11*4], eax
    inc r9
    jmp .merge_next

.merge_take_right:
    mov [rsi + r11*4], ebx
    inc r10

.merge_next:
    inc r11
    jmp .merge_loop

.merge_left_done:
    cmp r9, rcx
    jg .merge_right_phase

.merge_left_copy:
    mov eax, [rdi + r9*4]
    mov [rsi + r11*4], eax
    inc r9
    inc r11
    cmp r9, rcx
    jle .merge_left_copy

.merge_right_phase:
    cmp r10, r8
    jg .merge_writeback

.merge_right_copy:
    mov eax, [rdi + r10*4]
    mov [rsi + r11*4], eax
    inc r10
    inc r11
    cmp r10, r8
    jle .merge_right_copy

.merge_writeback:
    mov r9, rdx
.wb_loop:
    cmp r9, r8
    jg .wb_done
    mov eax, [rsi + r9*4]
    mov [rdi + r9*4], eax
    inc r9
    jmp .wb_loop
.wb_done:
    ret
