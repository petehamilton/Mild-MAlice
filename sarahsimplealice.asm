extern printf


LINUX        equ     80H      ; interupt number for entering Linux kernel
EXIT         equ     60       ; Linux system call 1 i.e. exit ()




section .data
    intfmt: db "%ld", 10, 0


segment .text
    global	main


main:
mov r8, 2
mov r9, 3
add r8, r9
push rdi
push rsi
mov rsi, r8
mov rdi, intfmt
xor rax, rax
call printf
pop rdi
pop rsi
test2:
pop r8
mov r9, 3
add r8, r9
mov eax r8
mov esp, ebp
pop ebp
ret
    call os_return		; return to operating system


os_return:
    mov  rax, EXIT		; Linux system call 1 i.e. exit ()
    mov  rdi, 0		; Error code 0 i.e. no errors
    int  LINUX		; Interrupt Linux kernel
