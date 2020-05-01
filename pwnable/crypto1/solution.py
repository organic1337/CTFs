import re
import socket
from typing import List


BLOCK_SIZE = 16
ALLOWED_CHARACTERS = '1234567890abcdefghijklmnopqrstuvwxyz-_'
COOKIE_LENGTH = 89


def get_encrypted(identity: str, password: str) -> List[str]:
    conn = socket.socket()
    conn.connect(('pwnable.kr', 9006))

    conn.send(f'{identity}\n'.encode())
    conn.send(f'{password}\n'.encode())

    conn.recv(1024)
    raw_response = conn.recv(1024).decode()

    encrypted_data = re.search(r'\((?P<encrypted>.*)\)', raw_response).group('encrypted')
    result = [encrypted_data[i:i + BLOCK_SIZE * 2] for i in range(0, len(encrypted_data), BLOCK_SIZE * 2)]
    # print(result)
    return result


def main():
    cookie = ''

    # C0 | C1 - C0 is junk block,  C1 is the cookie block
    p0 = 'a' * (BLOCK_SIZE - 1)
    encrypted_blocks = get_encrypted(p0, 'a' * (BLOCK_SIZE - 2))

    for block_index in range(1, len(encrypted_blocks) + 1):
        for i in range(1, BLOCK_SIZE + 1):
            prefix = 'a' * (BLOCK_SIZE - 1 - i)
            cookie_block = get_encrypted(p0, prefix)[block_index]

            for character in ALLOWED_CHARACTERS:
                guessed_block = get_encrypted(p0, f'{prefix}-{cookie + character}')[block_index]
                if guessed_block == cookie_block:
                    cookie += character
                    print(character, end='')
                    break

            if len(cookie) == COOKIE_LENGTH:
                break


if __name__ == '__main__':
    main()
