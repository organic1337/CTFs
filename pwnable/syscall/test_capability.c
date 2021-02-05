#include <stdbool.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>


bool is_capable() {
    return true;
}


int main() {
    printf("Is Capable: 0x%x\n", is_capable());
    return 0;
}
