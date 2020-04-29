#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char** argv) {
    printf("result = %d\n", strcmp("\xca\xfe\xba\xbe", getenv("\xde\xad\xbe\xef")));
}