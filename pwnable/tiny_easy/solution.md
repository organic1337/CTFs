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

Since ASLR is enabled, each time this address will be randomized.
so, in order to bypass it, we can just build our payload as follows:

```
<address><plenty_of_nops><shellcode>
```


This way, we increase the chance that the address will be at one of the nops.
Then it will just run until it reaches the shell code.


The code that runs the binary with the payload is in `run_with_payload.c`


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
