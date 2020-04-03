#include <unistd.h>
#include <stdio.h>

int main() {
   execve("Hello, World!", NULL, NULL);
   return 0;
}