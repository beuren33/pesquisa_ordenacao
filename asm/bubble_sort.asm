; bubble_sort.asm
; void bubble_sort(int32_t *arr, int64_t n)
; System V AMD64 ABI: rdi = arr, rsi = n
; Ordena em ordem crescente, com flag de "trocou" para encerrar cedo
; quando o vetor ja estiver ordenado (melhor caso O(n)).

section .text
global bubble_sort

bubble_sort:
    push rbp
    mov rbp, rsp

    cmp rsi, 2
    jl .done                   ; n < 2 -> nada a fazer

    mov rcx, rsi
    dec rcx                    ; rcx = limite do laco externo (n-1)

.outer:
    cmp rcx, 0
    je .done

    xor r8, r8                 ; r8 = j = 0
    xor r9, r9                 ; r9 = trocou = 0

.inner:
    cmp r8, rcx
    jge .inner_done

    mov eax, [rdi + r8*4]      ; eax = arr[j]
    mov edx, [rdi + r8*4 + 4]  ; edx = arr[j+1]
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
    je .done                   ; nao trocou -> ja esta ordenado
    dec rcx
    jmp .outer

.done:
    pop rbp
    ret
