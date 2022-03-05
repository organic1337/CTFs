# Solution

Because of [C operatiors precedence](https://en.cppreference.com/w/c/language/operator_precedence)
the first thing to execute is the "<" operator, and then the "=" operator.
so what happens here:

```c
int fd;
if(fd=open("/home/mistake/password",O_RDONLY,0400) < 0){
    printf("can't open password %d\n", fd);
    return 0;
}
```

- `open` is called and returns 1
- `1 < 0` evaluates to 0
- `fd` is assigned with 0 (stdin)


and then our code reads the original password from stdin, and then
by using scanf it reads our password.

Each character of the second output is xored with 1.

```python
In [2]: chr(ord('A') ^ 1)
Out[2]: '@'
```

so we can just provide the following input:

- `AAAAAAAAAA`
- `@@@@@@@@@@`


and get the flag:

```
mistake@pwnable:~$ ./mistake
do not bruteforce...
AAAAAAAAAA
input password : @@@@@@@@@@
Password OK
Mommy, the operator priority always confuses me :(
```


