extern printf
extern fflush
extern malloc
extern free


LINUX        equ     80H      ; interupt number for entering Linux kernel
EXIT         equ     60       ; Linux system call 1 i.e. exit ()




section .data
    outputintfmt: db "%ld", 0


segment .text
    global	main


main:

    mov r8, 8
    mov rdi, r8
    imul rdi, 8
    xor rax, rax
    call malloc
    add rsp, 8
    test rax, rax
    jz malloc_failure
    mov r8, rax
    
    mov r9, 7
    sub r9, 1
    imul r9, 8
    add r9, r8
    mov qword [r9], 100
    
    mov r13, 7
    sub r13, 1
    imul r13, 8
    add r13, r8
    
    
    push rdi
    push r8
    push rsi
    push r10
    mov rsi, [r13]
    push r9
    mov rdi, outputintfmt
    xor rax, rax
    call printf
    xor rax, rax
    call fflush
    pop r9
    pop r10
    pop rsi
    pop r8
    pop rdi
    malloc_failure:
    deallocate_start:
    dealloc_1:
    mov rdi, r8
    xor rax, rax
    call free
    deallocate_end:
    call os_return		; return to operating system


os_return:
    mov  rax, EXIT		; Linux system call 1 i.e. exit ()
    mov  rdi, 0		; Error code 0 i.e. no errors
    syscall		; Interrupt Linux kernel 64-bit
