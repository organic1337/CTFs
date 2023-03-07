#include <unistd.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <string.h>

#define MAX 10000

int main() {
    int counter = 0;
    int upper_syscall_descriptor = 223;
    int input = 0x800be90c;
    char output[MAX];
    memset(output, 0, MAX);
    
    // Read content
    while (counter < 1000) {
        syscall(upper_syscall_descriptor, input + counter, output);

        for (int i = 0; i < MAX && output[i] != 0; i++) {
            printf("%02x ", output[i]);
            counter++;
        }

        printf("00 ");
    }
    
}
