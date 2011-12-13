extern printf
extern scanf


LINUX        equ     80H      ; interupt number for entering Linux kernel
EXIT         equ     60       ; Linux system call 1 i.e. exit ()


section .bss
intinput resq 1
    overflow14: resq 1


section .data
    outputintfmt: db "%ld", 0
    outputstringfmt: db "%s", 0
    outputcharfmt: db "%c", 0
    inputintfmt: db "%ld", 0
    intfmt_message: db "Please enter an integer and press enter: ", 0
    sentence3: db "And if one green bottle should accidentally fall \n", 10, 0
    sentence5: db " green bottles hanging on the wall \n \n", 10, 0
    sentence2: db " green bottles hanging on the wall \n", 10, 0
    sentence6: db "I am going to smash you, silly bottle! Then there will be no bottles left!\n", 10, 0
    sentence1: db " green bottles hanging on the wall \n", 10, 0
    sentence4: db "There would be ", 10, 0
    sentence0: db "How many bottles were there on the wall?\n", 10, 0


segment .text
    global	main


main:
    mov r8, sentence0
    push rdi
    push rsi
    push r10
    push r9
    mov rsi, r8
    mov rdi, outputstringfmt
    xor rax, rax
    call printf
    pop r9
    pop r10
    pop rsi
    pop rdi
    push r8
    push rdi
    push rsi
    push r10
    push r9
    mov rsi, intfmt_message
    mov rdi, outputstringfmt
    xor rax, rax
    call printf
    pop r9
    pop r10
    pop rsi
    pop rdi
    pop r8
    push rdi
    push r8
    push rsi
    push r10
    mov rsi, intinput
    mov rdi, inputintfmt
    xor rax, rax
    call scanf
    mov r9, [intinput]
    pop r10
    pop rsi
    pop r8
    pop rdi
    loop_start_1:
    mov r8, r9
    mov r10, 1
    logical_eval_start_3:
    cmp r8, r10
    je logical_eval_true_4
    mov r8, 0
    jmp logical_eval_end_5
    logical_eval_true_4:
    mov r8, 1
    logical_eval_end_5:
    cmp r8, 0
    jne loop_end_2
    mov r8, r9
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
    mov r8, sentence1
    push rdi
    push rsi
    push r10
    push r9
    mov rsi, r8
    mov rdi, outputstringfmt
    xor rax, rax
    call printf
    pop r9
    pop r10
    pop rsi
    pop rdi
    mov r8, r9
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
    mov r8, sentence2
    push rdi
    push rsi
    push r10
    push r9
    mov rsi, r8
    mov rdi, outputstringfmt
    xor rax, rax
    call printf
    pop r9
    pop r10
    pop rsi
    pop rdi
    mov r8, sentence3
    push rdi
    push rsi
    push r10
    push r9
    mov rsi, r8
    mov rdi, outputstringfmt
    xor rax, rax
    call printf
    pop r9
    pop r10
    pop rsi
    pop rdi
    dec r9
    mov r8, sentence4
    push rdi
    push rsi
    push r10
    push r9
    mov rsi, r8
    mov rdi, outputstringfmt
    xor rax, rax
    call printf
    pop r9
    pop r10
    pop rsi
    pop rdi
    mov r8, r9
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
    mov r8, sentence5
    push rdi
    push rsi
    push r10
    push r9
    mov rsi, r8
    mov rdi, outputstringfmt
    xor rax, rax
    call printf
    pop r9
    pop r10
    pop rsi
    pop rdi
    jmp loop_start_1
    loop_end_2:
    mov r8, sentence6
    push rdi
    push rsi
    push r10
    push r9
    mov rsi, r8
    mov rdi, outputstringfmt
    xor rax, rax
    call printf
    pop r9
    pop r10
    pop rsi
    pop rdi
    call os_return		; return to operating system


os_return:
    mov  rax, EXIT		; Linux system call 1 i.e. exit ()
    mov  rdi, 0		; Error code 0 i.e. no errors
    syscall		; Interrupt Linux kernel 64-bit
