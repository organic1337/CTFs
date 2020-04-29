/*
Solution for pwnable.kr input challenge.
*/
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#define ELF_PATH "/home/input2/input"
#define PORT "8000"
#define ARGV_LENGTH 100


int main() {
    // Stage 1 solution - 
    // Put 100 args in the argv array given by the argv_ptr argument.
    // sets the values at indexes 'A' and 'B' to special values. These
    // special values appear in the elf source code (input.c).
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


    // Stage 2 solution - 
    // Ok so here we need to provide input throught standard input and standard error,
    // This is since in input.c we see the "read" function called one time with 0 (stdin),
    // and one time with 2 (stderr). What we can do is open a new pipe using the pipe() function,
    // then we just write to the pipe 2 values:
    //  1) "\x00\x0a\x00\xff" - The elf file expects to read this value from stdin first
    //  2) "\x00\x0a\x02\xff" - The elf file expects to read this value from stderr
    // 
    // Then we just free stdin and stderr, and put our pipe to replace them.
    const char solution2_input[] = "\x00\x0a\x00\xff\x00\x0a\x02\xff";
    
    // Create 2 pipes, one for reading, one for writing
    int pipes[2];
    pipe(pipes);
    const int read_pipe = pipes[0], write_pipe = pipes[1];
    
    // Write the wanted input to the pipe
    write(write_pipe, solution2_input, sizeof(solution2_input));
    
    // Replace the stdin pipe with our read pipe 
    dup2(read_pipe, STDIN_FILENO);
    dup2(read_pipe, STDERR_FILENO);


    // Stage 3 solution -
    // The elf file is just looking for a specific environment variable, with a specific value,
    // What we can do is use putenv to set the environment variable it expects.
    // it actually works because putenv changes the environment variables for the process.
    // Note that what execv does is simply run something on the same process, instead of what
    // was running before calling it. It actually 'replaces' the running program with another.
    putenv("\xde\xad\xbe\xef=\xca\xfe\xba\xbe");


    // Stage 4 solution -
    // In this stage we can see that input.c looks or a file named "\x0a", what we can
    // do is just Create a file with this name, write the data that input.c expects to
    // see into this file.
    char stage4_input[] = "\x00\x00\x00\x00";
    FILE* stage4_input_fd = fopen("\x0a", "w");
    fwrite(stage4_input, sizeof(char), sizeof(stage4_input), stage4_input_fd);
    fclose(stage4_input_fd);


    // Stage 5 solution -
    // For stage 5 we can just use netcat as follows
    // echo -ne "\xde\xad\xbe\xef" | nc 127.0.0.1 8000


    int exec_result = execv(ELF_PATH, (char* const*)argv);
    printf("Exec exited with code: %d\nErrno: %d", exec_result);
}