#include <stdint.h>

int main() {
    int dummy = 0;

    // ⬇️ chỉ duy nhất vòng này, literal bound
    #pragma cgra acc
    for (int idx = 17; idx < 239; idx++) {
        // đơn giản hóa: dummy = dummy + idx
        dummy = dummy + idx;
    }

    return dummy;
}
