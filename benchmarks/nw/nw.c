#include <stdint.h>
#define LEN 64
#define MATCH 2
#define MISMATCH -1
#define GAP 1
static int8_t seqA[LEN] = { 'A','C','G','T' };
static int8_t seqB[LEN] = { 'A','C','G','T' };
static int32_t prev_row[LEN+1];
static int32_t curr_row[LEN+1];

int main() {
    // Initialize first row
    for (int j = 0; j <= LEN; j++) prev_row[j] = -GAP * j;

    #pragma cgra acc
    for (int j = 1; j <= LEN; j++) {
        int diag = prev_row[j-1] + (seqA[j-1] == seqB[j-1] ? MATCH : MISMATCH);
        int up   = prev_row[j] - GAP;
        int left = curr_row[j-1] - GAP;
        int m = diag;
        if (up > m) m = up;
        if (left > m) m = left;
        curr_row[j] = m;
    }

    return 0;
}