# Leg

## Binary information

- ARM architecture
- C source code available


## What the code does

Simply asks for a key, if the key is right, it prints the flag.
Otherwise, just print a message.

```
$ ./leg                       
Daddy has very strong arm!: 123123     
I have strong leg :P
```

## Notes

### Running flow
- Ask the user for a `key` (of type int)
- Run 3 functions, `key1`, `key2`, `key3`
- Sum their return values
- Compare the sum to the integer `key`
- If equals: Print the flag, else: print `I have strong leg :P`

All that needs to be done is discovering what `key1`, `key2`, and `key3` return.


### ARM useful info

**Calling convention**

In arm 32 bit, the calling convention is as follows:
- `r15` ( = Program Counter = pc) - Holds the address of the next instructin to be executed. In case an address is assigned to that
  register, the execution will jump to that address.
- `r14` (Link register) - The `BL` instruction is used in a subroutine call and stores the return address in this register
- `r13` (Stack pointer)
- `r12`
- `r4` - `r11` - Local variables
- `r0` - `r3` - Argument values passed to a function or return value

**`bx` instruction**

`bx` - Branch and eXchange instruction set

ARM cpus (with T in their names, such as `ARM7 TDMI`) has 2 modes: ARM or THUMB. THUMB mode contains 16 bit wide instructions while ARM contains 32 bits wide instructions. In thumb mode, the code may be smaller and faster if the target has slow memory.

bx command is used for switching between the two. if the LSB (Least Significant Bit) is 1, Thumb mode is used, else, ARM


### What the functions actually return?


**`key1` function**

```C
int key1() {
    asm("mov r3, pc")
};
```

This function return the value inside `pc` register, which is the address of the next insturction to be executed:

```
Dump of assembler code for function key1:
   0x00008cd4 <+0>:	push	{r11}		; (str r11, [sp, #-4]!)
   0x00008cd8 <+4>:	add	r11, sp, #0
   0x00008cdc <+8>:	mov	r3, pc
   0x00008ce0 <+12>:	mov	r0, r3
   0x00008ce4 <+16>:	sub	sp, r11, #0
   0x00008ce8 <+20>:	pop	{r11}		; (ldr r11, [sp], #4)
   0x00008cec <+24>:	bx	lr
```

Return value: `0x8ce4`

**`key2` function**
```C
int key2(){
	asm(
	"push	{r6}\n"
	"add	r6, pc, $1\n"
	"bx	r6\n"
	".code   16\n"
	"mov	r3, pc\n"
	"add	r3, $0x4\n"
	"push	{r3}\n"
	"pop	{pc}\n"
	".code	32\n"
	"pop	{r6}\n"
	);
}
```

```asm
   0x00008cf0 <+0>:	push	{r11}		; (str r11, [sp, #-4]!)
   0x00008cf4 <+4>:	add	r11, sp, #0
   0x00008cf8 <+8>:	push	{r6}		; (str r6, [sp, #-4]!)
   0x00008cfc <+12>:	add	r6, pc, #1
   0x00008d00 <+16>:	bx	r6
   0x00008d04 <+20>:	mov	r3, pc
   0x00008d06 <+22>:	adds	r3, #4
   0x00008d08 <+24>:	push	{r3}
   0x00008d0a <+26>:	pop	{pc}
   0x00008d0c <+28>:	pop	{r6}		; (ldr r6, [sp], #4)
   0x00008d10 <+32>:	mov	r0, r3
   0x00008d14 <+36>:	sub	sp, r11, #0
   0x00008d18 <+40>:	pop	{r11}		; (ldr r11, [sp], #4)
   0x00008d1c <+44>:	bx	lr
```

Now the function returns `pc` in line 6 plus 4.

Return value: `0x8d08 + 4`


**`key3` function**
```C
int key3(){
	asm("mov r3, lr\n");
}
```

According to ARM calling convention, `lr` holds the return address of the function.


```
; Call to "key3" inside main
   0x00008d78 <+60>:	add	r4, r4, r3
   0x00008d7c <+64>:	bl	0x8d20 <key3>
   0x00008d80 <+68>:	mov	r3, r0
   0x00008d84 <+72>:	add	r2, r4, r3
```
Return value: `0x8d80`


## Solution
The key is the sum of the return values of:
- `key1`: 0x8ce0
- `key2`: 0x8d06 + 4
- `key3`: 0x8d80


```python
In [1]: key1 = 0x8ce4

In [2]: key2 = 0x8d08 + 4

In [3]: key3 = 0x8d80

In [4]: print(key1 + key2 + key3)
108400
```

```
$ ./leg
Daddy has very strong arm! : 108400
Congratz!
My daddy has a lot of ARMv5te muscle!
```
