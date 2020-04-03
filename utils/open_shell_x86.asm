open_shell:
    ; Retreive the string address from the caller
    ; IP value
    pop ebx
    push ebx
    add bx, 4

    mov eax, 0xb
    xor ecx, ecx
    xor edx, edx
    int 80h

    ret

caller:
    call open_shell
    db "/bin/sh", 0