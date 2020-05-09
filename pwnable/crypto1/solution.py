import re
import socket
from typing import List
from hashlib import sha256

BLOCK_SIZE = 16
ALLOWED_CHARACTERS = '1234567890abcdefghijklmnopqrstuvwxyz-_'
COOKIE_LENGTH = 49


def get_encrypted(identity: str, password: str) -> List[str]:
    conn = socket.socket()
    conn.connect(('pwnable.kr', 9006))

    conn.send(f'{identity}\n'.encode())
    conn.send(f'{password}\n'.encode())

    conn.recv(1024)
    raw_response = conn.recv(1024).decode()

    encrypted_data = re.search(r'\((?P<encrypted>.*)\)', raw_response).group('encrypted')
    result = [encrypted_data[i:i + BLOCK_SIZE * 2] for i in range(0, len(encrypted_data), BLOCK_SIZE * 2)]

    return result


def find_cookie() -> str:
    """
    In order to find the cookie we rely on a few exploits on the given cryptosystem:
    - The IV is a constant value
    - We are in position of Chosen-Plaintext-Attackers. We can send any
      plaintext we get and view the ciphertext.

    This attack follows the same principles of well known attacks such as BEAST
    attack on TLS.

    This is exactly how we do it:
     - First, we create a block by filling it with 15 bytes, and then we're left
       with one byte from the cookie. So what we do is calculating the value of the
       real block, and then repeatedly guessing the first byte of the cookie until
       the real ciphertext matches our guessed ciphertext

     - Then we do the same thing for the rest of the blocks, until we found all the
       characters of the cookie.

    This methods lets us find the cookie in complexity in n * 256 iterations instead
    of just 256 ** n.

    :return: The Cookie we calculated
    """
    cookie = ''
    junk_block = 'a' * (BLOCK_SIZE - 1)

    # Start from block index 1
    block_index = 1

    # Iterate through all the blocks and stop until the whole cookie
    # is found
    while True:
        # Find the next 15 bytes
        for byte_index in range(1, BLOCK_SIZE):
            prefix = 'a' * (BLOCK_SIZE - 1 - byte_index + (block_index - 1))
            cookie_block = get_encrypted(junk_block, prefix)[block_index]

            for character in ALLOWED_CHARACTERS:
                guessed_data = f'{prefix}-{cookie + character}'
                guessed_block = get_encrypted(junk_block, guessed_data)[block_index]

                if guessed_block == cookie_block:
                    cookie += character
                    # TODO: Remove this print
                    print(character, end='')
                    break

            if len(cookie) == COOKIE_LENGTH:
                return cookie

        # Progress the block index
        block_index += 1


def main():
    """
    Prints the admin password for pwnable.kr crypto1
    challange.
    """
    cookie = find_cookie()
    admin_password = sha256(b'admin' + cookie.encode()).hexdigest()
    print(f'The admin password is: \n{admin_password}')


if __name__ == '__main__':
    main()
