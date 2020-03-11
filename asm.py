from pwnlib import asm


FILE_NAME = ''
CONTENT_LENGTH = 100


def main():
    asm.asm(f'''
    jmp start
    
    main:        
        pop rdi
        push rdi       
        
        push rbp
        mov rbp, rsp
        sub rsp, {CONTENT_LENGTH}
        
        ; Open the file 
        mov rsi, O_RDONLY 
        mov rdx, O_IRUSR
        mov rax, SYS_OPEN 
        syscall

        mov rdi, eax
        mov rsi, [rbp - {CONTENT_LENGTH}]
        mov rdx, {CONTENT_LENGTH}
        mov rax, SYS_READ
        syscall

        mov rdi, STDOUT 
        mov rsi, [rbp - {CONTENT_LENGTH}]
        mov rdx, {CONTENT_LENGTH}
        mov rax, SYS_WRITE
        syscall

        mov rsp, rbp
        pop rbp
        ret 

    start:
        call main
        .asciz {FILE_NAME}
    ''')


if __name__ == '__main__':
    main()
