#include <stdbool.h>
#include <stdio.h>
#include <sys/types.h>


bool is_capable(uid_t uid) {
    return true;
}


int main() {
    printf("Is Capable: 0x%x\n", is_capable(1000));
    return 0;
}
