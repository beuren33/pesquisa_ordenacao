; quick_sort.asm
; void quick_sort(int32_t *arr, int64_t n)
; System V AMD64 ABI: rdi = arr, rsi = n
; Quicksort recursivo com particionamento de Lomuto (pivo = ultimo elemento).

section .text
global quick_sort

quick_sort:
    cmp rsi, 2
    jl .done                   ; n < 2 -> nada a fazer

    push rbp
    mov rbp, rsp

    mov rdx, rsi
    dec rdx                     ; hi = n - 1
    xor rsi, rsi                ; lo = 0
    call .qsort_rec

    pop rbp
.done:
    ret

; .qsort_rec(arr=rdi, lo=rsi, hi=rdx) -- recursivo
; Sempre recursa no lado menor da particao e faz loop no lado maior, para
; limitar a profundidade de recursao a O(log n) mesmo no pior caso (array
; ja ordenado/invertido) -- sem isso a pilha estoura em datasets grandes.
.qsort_rec:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14

    mov rbx, rdi                ; arr
    mov r12, rsi                ; lo
    mov r13, rdx                ; hi

.qs_loop:
    cmp r12, r13
    jge .rec_done                ; lo >= hi -> nada a fazer

    mov rdi, rbx
    mov rsi, r12
    mov rdx, r13
    call .partition
    mov r14, rax                 ; p

    mov rax, r14
    sub rax, r12                  ; tamanho esquerda = p - lo
    mov rcx, r13
    sub rcx, r14                  ; tamanho direita = hi - p
    cmp rax, rcx
    jl .left_smaller

    ; direita <= esquerda: recursa na direita, loop na esquerda
    mov rdi, rbx
    lea rsi, [r14 + 1]
    mov rdx, r13
    call .qsort_rec
    mov r13, r14
    dec r13                       ; hi = p - 1
    jmp .qs_loop

.left_smaller:
    ; esquerda < direita: recursa na esquerda, loop na direita
    mov rdi, rbx
    mov rsi, r12
    lea rdx, [r14 - 1]
    call .qsort_rec
    mov r12, r14
    inc r12                        ; lo = p + 1
    jmp .qs_loop

.rec_done:
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

; .partition(arr=rdi, lo=rsi, hi=rdx) -> rax = posicao final do pivo
; Pivo = mediana entre arr[lo], arr[mid], arr[hi], colocado em arr[hi] antes
; de particionar -- sem isso, pivo fixo (ultimo elemento) degrada pra O(n^2)
; de verdade em dataset ja ordenado/invertido (nao so estoura pilha).
.partition:
    mov r8, rdx
    sub r8, rsi
    sar r8, 1
    add r8, rsi                  ; mid = lo + (hi-lo)/2

    mov eax, [rdi + rsi*4]       ; arr[lo]
    mov ecx, [rdi + r8*4]        ; arr[mid]
    mov r9d, [rdi + rdx*4]       ; arr[hi]

    cmp eax, ecx
    jle .med_lo_le_mid
    ; mid < lo: troca lo/mid pra manter eax<=ecx
    xchg eax, ecx
.med_lo_le_mid:
    cmp ecx, r9d
    jle .med_mid_le_hi
    ; hi < mid: mid = hi
    mov ecx, r9d
    cmp eax, ecx
    jle .med_mid_le_hi
    mov ecx, eax
.med_mid_le_hi:
    ; ecx = mediana(arr[lo], arr[mid], arr[hi]); coloca em arr[hi]
    mov r9d, [rdi + rdx*4]
    cmp r9d, ecx
    je .med_done
    ; acha onde ecx estava (lo, mid ou hi) e troca com hi
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
    mov r9d, ecx                 ; pivot = mediana (ja esta em arr[hi])
    mov r10, rsi
    dec r10                       ; i = lo - 1
    mov r11, rsi                  ; j = lo

.part_loop:
    cmp r11, rdx
    jge .part_after
    mov eax, [rdi + r11*4]        ; arr[j]
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
