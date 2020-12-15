#include <unistd.h>
#include <stdlib.h>
#include <time.h>
#include <stdio.h>

/**
 * Simulate the custom hash function of the md5_calculator challenge in
 * pwnable.kr.
 *
 * The hash function works as follow:
 *  - Generate 8 random numbers by using rand().
 *  - Sum all the generated numbers instead of the 1st.
 *  - Return the result
 *
 * @param result: The Result hash (without the canary)
 * @return: 0 on success, -1 on error
 */
int custom_hash(uint* result) {
    uint random_numbers[8];

    for (int i = 0; i < 8; i++) {
        random_numbers[i] = rand();
    }

    (*result) = 0;
    (*result) += random_numbers[1] + random_numbers[5];
    (*result) += random_numbers[2] - random_numbers[3];
    (*result) += random_numbers[7];                         // + Canary in the original function
    (*result) += random_numbers[4] - random_numbers[6];

    return 0;
}

/**
 * Receive the random seed as an argument.
 */
int main(int argc, char** argv) {
    if (argc != 2) {
        printf("Usage: %s [srand seed]\n", argv[0]);
        exit(1);
    }

    int seed = atoi(argv[1]);
    srand(seed);

    uint result;
    custom_hash(&result);

    printf("%d", result);
    return 0;
}
