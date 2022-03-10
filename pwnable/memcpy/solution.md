# MEMCPY



I compiled it using the comment on the first line on the source code (compiled
it on the remote), and then ran it inside GDB.

Let's try to give it some valid input:


```
Starting program: /tmp/organic/memcpy
Hey, I have a boring assignment for CS class.. :(
The assignment is simple.
-----------------------------------------------------
- What is the best implementation of memcpy?        -
- 1. implement your own slow/fast version of memcpy -
- 2. compare them with various size of data         -
- 3. conclude your experiment and submit report     -
-----------------------------------------------------
This time, just help me out with my experiment and get flag
No fancy hacking, I promise :D
specify the memcpy amount between 8 ~ 16 : 8
specify the memcpy amount between 16 ~ 32 : 16
specify the memcpy amount between 32 ~ 64 : 32
specify the memcpy amount between 64 ~ 128 : 64
specify the memcpy amount between 128 ~ 256 : 128
specify the memcpy amount between 256 ~ 512 : 256
specify the memcpy amount between 512 ~ 1024 : 512
specify the memcpy amount between 1024 ~ 2048 : 1024
specify the memcpy amount between 2048 ~ 4096 : 2048
specify the memcpy amount between 4096 ~ 8192 : 4096
ok, lets run the experiment with your configuration
experiment 1 : memcpy with buffer size 8
ellapsed CPU cycles for slow_memcpy : 2062
ellapsed CPU cycles for fast_memcpy : 196

experiment 2 : memcpy with buffer size 16
ellapsed CPU cycles for slow_memcpy : 246
ellapsed CPU cycles for fast_memcpy : 198

experiment 3 : memcpy with buffer size 32
ellapsed CPU cycles for slow_memcpy : 308
ellapsed CPU cycles for fast_memcpy : 394

experiment 4 : memcpy with buffer size 64
ellapsed CPU cycles for slow_memcpy : 614
ellapsed CPU cycles for fast_memcpy : 122

experiment 5 : memcpy with buffer size 128
ellapsed CPU cycles for slow_memcpy : 918

Program received signal SIGSEGV, Segmentation fault.
0x080487cc in fast_memcpy ()
(gdb) bt
#0  0x080487cc in fast_memcpy ()
#1  0x08048b65 in main ()
```

we get a segfault, at address 0x80487cc in `fast_memcpy` function.
the error occures in the following line:

```asm
movntps XMMWORD PTR [edx],xmm0
```


Appearantly, the movntps instruction requires the value inside `edx` to be aligned with 16 bit,
and this is why we get the segfault.


We can of course effect the alignment because we have the power to determine the allocated size each iteration of the loop.

The following sizes will do the job:

```
8
32
48
72
152
504
1016
2040
4088
4096
```


flag: `1_w4nn4_br34K_th3_m3m0ry_4lignm3nt`

