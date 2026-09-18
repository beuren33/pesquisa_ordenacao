extern malloc
extern free

section .text
global radix_sort

radix_sort:
    cmp rsi, 2
    jl .done

    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp, 8

    mov rbx, rdi
    mov r12, rsi

    mov rdi, r12
    shl rdi, 2
    call malloc wrt ..plt
    mov r13, rax

    add rsp, 8
    sub rsp, 2048

    xor r14, r14

.pass_loop:
    cmp r14, 32
    jge .passes_done

    mov rdi, rsp
    xor rax, rax
    mov rcx, 256
.zero_loop:
    mov [rdi], rax
    add rdi, 8
    dec rcx
    jnz .zero_loop

    xor r15, r15
.count_loop:
    cmp r15, r12
    jge .count_done
    mov eax, [rbx + r15*4]
    mov ecx, r14d
    shr eax, cl
    and eax, 0xFF
    inc qword [rsp + rax*8]
    inc r15
    jmp .count_loop
.count_done:

    mov rcx, 1
.prefix_loop:
    cmp rcx, 256
    jge .prefix_done
    mov rax, rcx
    dec rax
    mov rax, [rsp + rax*8]
    add [rsp + rcx*8], rax
    inc rcx
    jmp .prefix_loop
.prefix_done:

    mov r15, r12
    dec r15
.place_loop:
    cmp r15, 0
    jl .place_done
    mov eax, [rbx + r15*4]
    mov edx, eax
    mov ecx, r14d
    shr edx, cl
    and edx, 0xFF
    dec qword [rsp + rdx*8]
    mov rcx, [rsp + rdx*8]
    mov [r13 + rcx*4], eax
    dec r15
    jmp .place_loop
.place_done:

    xor r15, r15
.copy_loop:
    cmp r15, r12
    jge .copy_done
    mov eax, [r13 + r15*4]
    mov [rbx + r15*4], eax
    inc r15
    jmp .copy_loop
.copy_done:

    add r14, 8
    jmp .pass_loop

.passes_done:
    add rsp, 2048
    sub rsp, 8
    mov rdi, r13
    call free wrt ..plt
    add rsp, 8

    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
.done:
    ret
