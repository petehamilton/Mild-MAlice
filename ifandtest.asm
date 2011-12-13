extern printf


LINUX        equ     80H      ; interupt number for entering Linux kernel
EXIT         equ     60       ; Linux system call 1 i.e. exit ()




section .data
    outputintfmt: db "%ld", 0


segment .text
    global	main


main:
    mov r8, 9
    mov r9, 10
    mov r8, r9
    conditional_start_1:
    mov r9, 0
    logical_eval_start_4:
    cmp r8, r9
    je logical_eval_true_5
    mov r8, 0
    jmp logical_eval_end_6
    logical_eval_true_5:
    mov r8, 1
    logical_eval_end_6:
    cmp r8, 0
    je conditional_next_3
    mov r8, 0
    push rdi
    push rsi
    push r10
    push r9
    mov rsi, r8
    mov rdi, outputintfmt
    xor rax, rax
    call printf
    pop r9
    pop r10
    pop rsi
    pop rdi
    jmp conditional_end_2
    conditional_next_3:
    mov r9, r8
    mov r10, 0
    logical_eval_start_7:
    cmp r9, r10
    jg logical_eval_true_8
    mov r9, 0
    jmp logical_eval_end_9
    logical_eval_true_8:
    mov r9, 1
    logical_eval_end_9:
    mov r10, 0
    logical_eval_start_10:
    cmp r8, r10
    je logical_eval_true_11
    mov r8, 0
    jmp logical_eval_end_12
    logical_eval_true_11:
    mov r8, 1
    logical_eval_end_12:
    and r9, r8
    cmp r9, 0
    je conditional_end_2
    mov r10, 1
    push rdi
    push r8
    push rsi
    push r9
    mov rsi, r10
    mov rdi, outputintfmt
    xor rax, rax
    call printf
    pop r9
    pop rsi
    pop r8
    pop rdi
    conditional_end_2:
    call os_return		; return to operating system


os_return:
    mov  rax, EXIT		; Linux system call 1 i.e. exit ()
    mov  rdi, 0		; Error code 0 i.e. no errors
    syscall		; Interrupt Linux kernel 64-bit
