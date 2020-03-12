import itertools
from typing import Generator


BYTES_ORDER = 'little'


def pwnable_hash(plaintext: bytes) -> int:
    """
    Hashes a plaintext according to pwnable hash function
    """
    hashcode = 0
    for i in range(0, 20, 4):
        hashcode += int.from_bytes(plaintext[i:i + 4], BYTES_ORDER)

    return hashcode


def find_collisions(hashcode: int) -> Generator[bytes, None, None]:
    for subset in itertools.combinations(range(128), 20):
        formatted_combination = bytes(subset)
        print(formatted_combination)
        if pwnable_hash(formatted_combination) == hashcode:
            yield formatted_combination


def main():
    hashcode = 568134124
    average_dword = (hashcode + 1) // 5

    collision = average_dword.to_bytes(4, BYTES_ORDER) * 4
    collision += (average_dword - 1).to_bytes(4, BYTES_ORDER)

    hashed_collision = hex(pwnable_hash(collision))
    print(f'Hash: {hashed_collision}')
    print(f'Collision: {collision}')


if __name__ == '__main__':
    main()