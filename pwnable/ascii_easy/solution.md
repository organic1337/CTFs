# ASCII Easy

```
We often need to make 'printable-ascii-only' exploit payload.  You wanna try?

hint : you don't necessarily have to jump at the beggining of a function. try to land anyware.
```

Interesting...


```bash
ascii_easy@pwnable:~$ ls
ascii_easy  ascii_easy.c  flag  intended_solution.txt  libc-2.15.so
ascii_easy@pwnable:~$ ./ascii_easy
usage: ascii_easy [ascii input]
ascii_easy@pwnable:~$ ./ascii_easy hello_world
triggering bug...
ascii_easy@pwnable:~$ ./ascii_easy AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa
triggering bug...
Segmentation fault (core dumped)
ascii_easy@pwnable:~$
```

## Binary Information

```bash
$ file ascii_easy
ascii_easy: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=3a74cff7b340c23d3f90db3d934c4ca328c4a6b8, not stripped
$ checksec ascii_easy
[*] '/media/or/organic_drive/disk_content/workspace/ctfs/pwnable/ascii_easy/ascii_easy'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```



### Research

The binary loads libc library by using mmap with a fixed base
address, so ASLR is not a concern:


```C

#define BASE ((void*)0x5555e000)

void main(int argc, char* argv[]){
    ...
    int fd = open("/home/ascii_easy/libc-2.15.so", O_RDONLY);
    
    ...

    if (mmap(BASE, len_file, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_PRIVATE, fd, 0) != BASE){
        ...
    }
```


and ascii validation is applied to our input:

```C
int is_ascii(int c){
    if(c>=0x20 && c<=0x7f) return 1;
    return 0;
}
```

So we need to find ascii printable gadgets.



EXECV address is: `0x5555e000`


```
Breakpoint 1, 0x08048532 in vuln ()
(gdb) x/1s $edx                                                                                                                                                                                             
0xffe33bb0:     "@gaU/bin/sh"
```
ROPgadget --binary ./libc-2.15.so --offset 0x5555e000 --badbytes "00-1f|80-ff > gadgets.txt

```


