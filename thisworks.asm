extern printf
section .data
    char: db 'a'
    result: dq 1
    ;fmt: db  "%ld", 10, 0 FOR INT
    fmt: db "%c", 10, 0
    
    

segment .text
	global	main

LINUX  	equ     80H		; interupt number for entering Linux kernel
EXIT   	equ     1		; Linux system call 1 i.e. exit ()
WRITE	equ	4		; Linux system call 4 i.e. write ()
STDOUT	equ	1		; File descriptor 1 i.e. standard output

main:
    mov rsi, [char]
    mov rdi, fmt
    xor rax, rax
    call printf

    ;mov rcx, char
    ;push rcx
    ;mov rax, WRITE
    ;mov rbx, STDOUT
    ;mov rcx, rsp
    ;add rcx, 8
    ;mov rdx, 1
    ;int LINUX


    call os_return		; return to operating system

; ------------------------

os_return:
	mov  rax, EXIT		; Linux system call 1 i.e. exit ()
	mov  rbx, 0		; Error code 0 i.e. no errors
	int  LINUX		; Interrupt Linux kernel

