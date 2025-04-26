#include <stdint.h>
#define N 256
#define A 1103515245u
#define C 12345u
#define M 2147483648u
static uint32_t state = 1;

int main() {
    #pragma cgra acc
    for (int i = 0; i < N; i++) {
        // Linear congruential generator
        state = (A * state + C) % M;
    }
    return 0;
}