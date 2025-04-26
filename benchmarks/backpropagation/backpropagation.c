#include <stdint.h>
#define N 128
#define LR 1  // learning rate (scaled integer)
static int32_t weight[N];
static int32_t input_val[N];
static int32_t error_val[N];

int main() {
    // Initialize arrays (in real use-case, values come from data)
    for (int i = 0; i < N; i++) {
        weight[i] = 1000;
        input_val[i] = i;
        error_val[i] = N - i;
    }

    #pragma cgra acc
    for (int i = 0; i < N; i++) {
        // weight update: w += lr * error * input
        weight[i] += LR * error_val[i] * input_val[i];
    }

    return 0;
}