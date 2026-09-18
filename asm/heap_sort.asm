section .text
global heap_sort

heap_sort:
    cmp rsi, 2
    jl .done

    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13

    mov rbx, rdi
    mov r12, rsi

    mov rax, r12
    sar rax, 1
    dec rax
.build_loop:
    mov rdi, rbx
    mov rsi, r12
    mov rdx, rax
    push rax
    call .sift_down
    pop rax
    dec rax
    cmp rax, 0
    jge .build_loop

    mov r13, r12
    dec r13
.extract_loop:
    cmp r13, 0
    jle .extract_done

    mov eax, [rbx]
    mov ecx, [rbx + r13*4]
    mov [rbx], ecx
    mov [rbx + r13*4], eax

    mov rdi, rbx
    mov rsi, r13
    xor rdx, rdx
    push r13
    call .sift_down
    pop r13

    dec r13
    jmp .extract_loop
.extract_done:

    pop r13
    pop r12
    pop rbx
    pop rbp
.done:
    ret

.sift_down:
    push rbx
    push r12
    push r13
    push r14
    push r15

    mov rbx, rdi
    mov r12, rsi
    mov r13, rdx

.sift_loop:
    mov r14, r13

    mov r15, r13
    shl r15, 1
    inc r15

    cmp r15, r12
    jge .check_right
    mov eax, [rbx + r15*4]
    mov ecx, [rbx + r14*4]
    cmp eax, ecx
    jle .check_right
    mov r14, r15

.check_right:
    mov rax, r13
    shl rax, 1
    add rax, 2

    cmp rax, r12
    jge .after_check
    mov ecx, [rbx + rax*4]
    mov edx, [rbx + r14*4]
    cmp ecx, edx
    jle .after_check
    mov r14, rax

.after_check:
    cmp r14, r13
    je .sift_done

    mov eax, [rbx + r13*4]
    mov ecx, [rbx + r14*4]
    mov [rbx + r13*4], ecx
    mov [rbx + r14*4], eax

    mov r13, r14
    jmp .sift_loop

.sift_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret
