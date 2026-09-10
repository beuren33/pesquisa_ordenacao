; heap_sort.asm
; void heap_sort(int32_t *arr, int64_t n)
; System V AMD64 ABI: rdi = arr, rsi = n
; Heap sort in-place: constroi max-heap, depois extrai o maior repetidamente.

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

    mov rbx, rdi                 ; arr
    mov r12, rsi                  ; n

    ; construir heap: for i = n/2 - 1 downto 0: sift_down(arr, n, i)
    mov rax, r12
    sar rax, 1
    dec rax                        ; i = n/2 - 1
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

    ; extrair: for i = n-1 downto 1: swap(arr[0],arr[i]); sift_down(arr, i, 0)
    mov r13, r12
    dec r13                        ; i = n-1
.extract_loop:
    cmp r13, 0
    jle .extract_done

    mov eax, [rbx]
    mov ecx, [rbx + r13*4]
    mov [rbx], ecx
    mov [rbx + r13*4], eax

    mov rdi, rbx
    mov rsi, r13                    ; novo tamanho do heap
    xor rdx, rdx                     ; raiz = 0
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

; .sift_down(arr=rdi, size=rsi, i=rdx)
.sift_down:
    push rbx
    push r12
    push r13
    push r14
    push r15

    mov rbx, rdi                  ; arr
    mov r12, rsi                   ; size
    mov r13, rdx                    ; i

.sift_loop:
    mov r14, r13                    ; largest = i

    mov r15, r13
    shl r15, 1
    inc r15                          ; l = 2*i + 1

    cmp r15, r12
    jge .check_right
    mov eax, [rbx + r15*4]
    mov ecx, [rbx + r14*4]
    cmp eax, ecx
    jle .check_right
    mov r14, r15                     ; largest = l

.check_right:
    mov rax, r13
    shl rax, 1
    add rax, 2                        ; r = 2*i + 2

    cmp rax, r12
    jge .after_check
    mov ecx, [rbx + rax*4]
    mov edx, [rbx + r14*4]
    cmp ecx, edx
    jle .after_check
    mov r14, rax                      ; largest = r

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
