.data
hello_world:
    .asciz "Hello, world\n"

len_hi = . - hello_world

.section .text
.global _start
_start:
    //Switch to thumb for smaller code
    .code 32
    add r0, pc, #1
    bx r0
    .code 16
    //write(1,&hello_world,strlen(hello_world));
    mov r0, #1
    ldr r1, =hello_world
    ldr r2, =len_hi
    mov r7, #4
    svc #0
    //exit(0)
    mov r7, #1
    svc #0