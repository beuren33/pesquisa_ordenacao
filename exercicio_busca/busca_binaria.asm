section .data
    nome_arquivo    db "alunos.txt", 0
    modo_leitura    db "r", 0
    fmt_int         db "%d", 0
    fmt_aluno       db "%31s %d", 0
    msg_pergunta    db "Digite o numero do aluno a buscar: ", 0
    fmt_saida_ok    db "Aluno encontrado: %s", 10, 0
    fmt_saida_erro  db "Aluno nao encontrado.", 10, 0
    erro_arquivo    db "Erro ao abrir arquivo.", 10, 0
    erro_limite     db "Erro: arquivo tem mais alunos do que o buffer suporta (max 1000000).", 10, 0
    vazia           db 0

section .bss

    MAX_ALUNOS equ 1000000
    v       resb 36*MAX_ALUNOS
    n       resd 1
    alvo    resd 1
    fp      resq 1

section .text
    global main
    extern fopen, fscanf, fclose, printf, scanf, exit

main:
    push rbp
    mov rbp, rsp

    lea rdi, [rel nome_arquivo]
    lea rsi, [rel modo_leitura]
    call fopen
    test rax, rax
    jz .erro_abrir
    mov [rel fp], rax

    mov rdi, [rel fp]
    lea rsi, [rel fmt_int]
    lea rdx, [rel n]
    xor eax, eax
    call fscanf

    mov eax, [rel n]
    cmp eax, MAX_ALUNOS
    jg .erro_limite

    xor r12d, r12d
.loop_leitura:
    mov eax, [rel n]
    cmp r12d, eax
    jge .fim_leitura

    mov eax, r12d
    imul rax, rax, 36
    lea r13, [rel v]
    add r13, rax

    mov rdi, [rel fp]
    lea rsi, [rel fmt_aluno]
    mov rdx, r13
    lea rcx, [r13+32]
    xor eax, eax
    call fscanf

    inc r12d
    jmp .loop_leitura

.fim_leitura:
    mov rdi, [rel fp]
    call fclose

    lea rdi, [rel msg_pergunta]
    xor eax, eax
    call printf

    lea rdi, [rel fmt_int]
    lea rsi, [rel alvo]
    xor eax, eax
    call scanf

    lea rdi, [rel v]
    mov esi, [rel n]
    mov edx, [rel alvo]
    call busca_binaria

    cmp byte [rax], 0
    je .nao_achou

    mov rsi, rax
    lea rdi, [rel fmt_saida_ok]
    xor eax, eax
    call printf
    jmp .fim

.nao_achou:
    lea rdi, [rel fmt_saida_erro]
    xor eax, eax
    call printf

.fim:
    xor edi, edi
    call exit

.erro_abrir:
    lea rdi, [rel erro_arquivo]
    xor eax, eax
    call printf
    mov edi, 1
    call exit

.erro_limite:
    mov rdi, [rel fp]
    call fclose
    lea rdi, [rel erro_limite]
    xor eax, eax
    call printf
    mov edi, 1
    call exit

busca_binaria:
    push rbx
    push r12

    mov r12d, edx

    xor ebx, ebx
    mov ecx, esi
    dec ecx

.bb_loop:
    cmp ebx, ecx
    jg .bb_nao_encontrado

    mov eax, ebx
    add eax, ecx
    cdq
    mov r8d, 2
    idiv r8d
    mov r9d, eax

    imul r10, rax, 36
    lea r11, [rdi + r10]
    mov eax, [r11+32]

    cmp eax, r12d
    je .bb_encontrado
    jl .bb_menor

    lea ecx, [r9d-1]
    jmp .bb_loop

.bb_menor:
    lea ebx, [r9d+1]
    jmp .bb_loop

.bb_encontrado:
    mov rax, r11
    pop r12
    pop rbx
    ret

.bb_nao_encontrado:
    lea rax, [rel vazia]
    pop r12
    pop rbx
    ret
