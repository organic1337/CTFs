# Horcruxes

## Binary information
 - Elf 32 bit, dynamically linked.
 - Stack check disabled :)


## Notes
### What the binary does

Generates 7 random numbers and let's us guess the sum of those numbers.
If we guess right, it prints the flag.

```
Voldemort concealed his splitted soul inside 7 horcruxes.
Find all horcruxes, and destroy it!

Select Menu:39
How many EXP did you earned? : 3
You'd better get more experience to kill Voldemort
```

### How the code works
- Ask the user for a number. 
- If the number equals one of the generated numbers, print the number. (Very low chance of it to occur)
- Ask the user for guessing the sum of the numbers
- If the user is right, print the flag. Else, quit.


**Finding the generated numbers**

The binary contains 7 interesting functions:
```C
void A();
void B();
void C();
void D();
void E();
void F();
void G();
```

Each function prints one of the generated random numbers. It should be possible to create a rop chain that will go to all of these functions and print all the generated values, then the sum can easily be calculated.

**Code flaws**

The flaws in the code is that gets is used on a 100 length char array. It can be used for overriding the return address of the function since there's no stack checking.


```C
char[100] sum_guess; 

// ---- snip ----

printf("How many EXP did you earned? : ");
gets(sum_guess);
```


**What the stack looks like in `ropme` function**

```
-----------------------------
        Return address
-----------------------------
   Saved base pointer (ebp)
-----------------------------
            var 1
-----------------------------
            var 2
-----------------------------
            var 3
-----------------------------
            var 4
-----------------------------
      100 bytes buffer
-----------------------------
```

That means we need to write 120 bytes Before reaching the function
return address.


**Functions Addresses**

Function addresses found by using `readelf -a horcruxes`:

```C
void A();  // 0x809fe4b
void B();  // 0x809fe6a
void C();  // 0x809fe89
void D();  // 0x809fea8
void E();  // 0x809fec7
void F();  // 0x809fee6
void G();  // 0x80a207c
```


## Solution

The solution can be found in `solution.py`. The solution was creating a rop chain that will execute all A, B, C ... functions, and then execute the ropme function again, so it will ask again for the `sum` guess. 

Then we just provide the sum based of all the outputs of the A, B, C ... functions.

```
You found "Nagini the Snake" (EXP +-1739044233)
You found "Harry Potter" (EXP +725295418)
Select Menu:
Calculated sum is: 1292497478
b'1292497478'
How many EXP did you earned? : Magic_spell_1s_4vad4_K3daVr4!
```

~pwned
