# pwnable.kr - `input` challenge

Hi everyone, in this writeup I'm trying to solve the "input" challenge. This challange is from the
toddlers bottle section in pwnable.kr. In this challange we have an elf file along with its C source code, what we need
to do is pass input in various ways in order to make the app print the flag. Basically we'll need to pass
input in 5 ways:
- Arguments vector (argv)
- Standard io
- Environment variables
- Files
- Network

We'll go though stage by stage and see how we can solve it.


### Overviewing the source code
By looking at the source code we're able to see all the stages that we need to pass in order to capture
the flag. We also see that it's not gonna be too easy, the target elf expects "\x00" to be passed as 
an argv. and that is something we can't do from the terminal. Ok so first let's try to pass stage 1.

### Stage 1 - argv
Let's take a look at the stage one code:
```C
// input.c

// argv
if(argc != 100) return 0;
if(strcmp(argv['A'],"\x00")) return 0;
if(strcmp(argv['B'],"\x20\x0a\x0d")) return 0;
printf("Stage 1 clear!\n");
```

Ok so here we see that we're supposed to pass 100 command line arguments, with argument at index 'A' (0x41) should
equal "\x00", and at index ('B') we can need to have "\x20\x0a\x0d". First thing I tried to do was looking for a
way to pass these args from the terminal. Apperantly you just cant pass nullbyte as an argument... the terminal
will ignore it. Then I've tried writing something in python, maybe something like:
```python
import subprocess
subprocess.Popen(["input", "arg1", "args2" ... "\x00", "0x20\x0a\x0d" ...)
```

That actually didn't work. I got the following exception:

```
ValueError: embedded null byte
```

Then I decided to give up a high level solution, and I started writing C. I could provide command line arguments 
using the [execv](https://linux.die.net/man/3/execv) syscall. Let's try it out:

```C
// solution.c

#define ARGV_LENGTH 100
char* argv[ARGV_LENGTH + 1];

for (int i = 0; i < ARGV_LENGTH; i++) {
    // Set argv['A'] to 00
    if (i == (int)'A') {
        argv[i] = "\x00";
    }
    // Set argv['B'] to \x20\x0a\x0d 
    else if (i == (int)'B') {
        argv[i] = "\x20\x0a\x0d";
    }
    else if (i == (int)'C') {
        // Port for stage 5 solution
        argv[i] = PORT;
    }
    else {
        argv[i] = "arg";
    }

}

// Add terminating NULL byte
argv[ARGV_LENGTH] = NULL;

execv(ELF_PATH, (char* const*)argv);
```

Once we run this we get:

```
Welcome to pwnable.kr
Let's see if you know how to give input to program
Just give me correct inputs then you will get the flag :)
Stage 1 clear!
```

Nice so we got stage 2.


### Stage 2 - stdio
Ok so here we need to provide input through the standard input and standard error.
Here the the code from input.c that's responsible for that:

```C
// input.c

// stdio
char buf[4];
read(0, buf, 4);
if(memcmp(buf, "\x00\x0a\x00\xff", 4)) return 0;
read(2, buf, 4);
if(memcmp(buf, "\x00\x0a\x02\xff", 4)) return 0;
printf("Stage 2 clear!\n");
```

We can see the "read" function called one time with 0 (stdin),
and one time with 2 (stderr). What we can do is open a new pipe using the pipe() function,
then we just write to the pipe 2 values:
-  `"\x00\x0a\x00\xff"` - The elf file expects to read this value from stdin first
-  `"\x00\x0a\x02\xff"` - The elf file expects to read this value from stderr

Then we just free stdin and stderr, and put our pipe to replace them.
That's actually exactly what [dup2](https://linux.die.net/man/2/dup2) does... it takes 2 file descriptors,
frees the second one, and sets the first one instead. For example dup2(4, 2)
will free the stderr (2), and will assign 4 (file descriptor) to be as the new stderr instead.

```C
// solution.c

const char solution2_input[] = "\x00\x0a\x00\xff\x00\x0a\x02\xff";

// create 2 pipes, one for reading, one for writing
int pipes[2];
pipe(pipes);
const int read_pipe = pipes[0], write_pipe = pipes[1];

// write the wanted input to the pipe
write(write_pipe, solution2_input, sizeof(solution2_input));

// replace the stdin pipe with our read pipe
dup2(read_pipe, stdin_fileno);
dup2(read_pipe, STDERR_FILENO);
```

### Stage 3 - env
This stage is the simplest one actually... In input.c source code we can see that it looks for an anvironment variable
with name of: `"\xde\xad\xbe\xef"`, and value: `"\xca\xfe\xba\xbe"`. Here is the code:

```C
// input.c

// env
if(strcmp("\xca\xfe\xba\xbe", getenv("\xde\xad\xbe\xef"))) return 0;
printf("Stage 3 clear!\n");
```

What we can do is just set a new environment variable, with the expected value and that's pretty much it.
so in order to do that we'll use the [putenv](http://man7.org/linux/man-pages/man3/putenv.3.html) function.
putenv takes a string in the format of: `var_name=value`. So we after we now that we can just write
something like this:

```C
// solution.c

putenv("\xde\xad\xbe\xef=\xca\xfe\xba\xbe");
```

Boom, it works. now we have:
```
Welcome to pwnable.kr
Let's see if you know how to give input to program
Just give me correct inputs then you will get the flag :)
Stage 1 clear!
Stage 2 clear!
Stage 3 clear!
```

### Stage 4 - files
In this stage we can see that input.c looks or a file named "\x0a", what we can
do is just Create a file with this name, write the data that input.c expects to
see into this file.

This is how input.c looks for the file:
```C
// input.c

// file
FILE* fp = fopen("\x0a", "r");
if(!fp) return 0;
if( fread(buf, 4, 1, fp)!=1 ) return 0;
if( memcmp(buf, "\x00\x00\x00\x00", 4) ) return 0;
fclose(fp);
printf("Stage 4 clear!\n");
```

And this is how we can create the file in order to pass this stage:

```C
// solution.c

char stage4_input[] = "\x00\x00\x00\x00";
FILE* stage4_input_fd = fopen("\x0a", "w");
fwrite(stage4_input, sizeof(char), sizeof(stage4_input), stage4_input_fd);
fclose(stage4_input_fd);
```
### Stage 5 - network
For this stage, input.c opens a listener on a port, given by argv at index 'C' (0x43), and expects 
a specific data to be sent to this listener. Here is the code:

```C
// input.c

// network
int sd, cd;
struct sockaddr_in saddr, caddr;
sd = socket(AF_INET, SOCK_STREAM, 0);
if(sd == -1){
	printf("socket error, tell admin\n");
	return 0;
}
saddr.sin_family = AF_INET;
saddr.sin_addr.s_addr = INADDR_ANY;
saddr.sin_port = htons( atoi(argv['C']) );
if(bind(sd, (struct sockaddr*)&saddr, sizeof(saddr)) < 0){
	printf("bind error, use another port\n");
		return 1;
}
listen(sd, 1);
int c = sizeof(struct sockaddr_in);
cd = accept(sd, (struct sockaddr *)&caddr, (socklen_t*)&c);
if(cd < 0){
	printf("accept error, tell admin\n");
	return 0;
}
if( recv(cd, buf, 4, 0) != 4 ) return 0;
if(memcmp(buf, "\xde\xad\xbe\xef", 4)) return 0;
printf("Stage 5 clear!\n");
```

Technically, this it wouldn't be so easy to solve with code since we use the `execv` syscall, which
replaces are running solution elf with the input elf. The input elf must be running in order for it to open a listener,
and then we will need to parallely open a client and send the data. Which means we would probably end up opening
another process that connects to the listener opened by input elf. 

Instead of implementing something that complicated we can just use netcat with `|` operator on shell.
What `|` does is as follows:

Lets say we have `command A | command B`, what that will actually happen is that 2 child processes will be
forked from the current process. process 1 runs command A, process 2 runs command B. command A's stdout will be
redirected to command B's stdin. If command B is reading from the stdin it'll just wait for command A writing to it.
The redirection of A stdout is made using [anonymous pipes](https://en.wikipedia.org/wiki/Anonymous_pipe). 

The point is that `|` operator opens 2 processes. You could demonstrate it by running `sleep 1 | sleep 1` and see that
you only sleep for 1 second, not 2.

So what we'll do in this step is just: `./solution > output | echo -ne "\xde\xad\xbe\xef\n" | nc 127.0.0.1 8000`


Notice that we dump the output to an output file, so it won't get redirected to echo.

### Final step
Ok so now after we passed all the stages we just should run our solution and we're good to go aren't we?
well nope. In order to run our code we need to move it to a folder inside /tmp, and then we compile and run it there.
After we run it we will see that we passed all stages, but no flag is printed... WTF!?!

```
Welcome to pwnable.kr
Let's see if you know how to give input to program
Just give me correct inputs then you will get the flag :)
Stage 1 clear!
Stage 2 clear!
Stage 3 clear!
Stage 4 clear!
Stage 5 clear!
```

Why is this happening? let's take a closer look at the code that's supposed to give us the flag:
```C
// input.c
system("/bin/cat flag");
```

Oh ok I see what's going on... the file `flag` is not in our working directory, we are now working on temp rememver?
What we could do about it is change the cwd, or even simpler, just create a symlink of the flag in our tmp dirctory.

This is what I did:
```bash
# Create a directory in temp so we could work on it
mkdir /tmp/my_directory
cd /tmp/my_directory

# Paste our solution source code from your machine 
nano solution.c

# Compile the solution.c code
gcc solution.c -o solution

# Create flag symlink in our directory
ln -s ~/flag

# Run the solution (with the netcat part)
./solution > output | echo -ne "\xde\xad\xbe\xef\n" | nc 127.0.0.1 8000

# show the output
cat output

# And now you'll see the flag :)
```
