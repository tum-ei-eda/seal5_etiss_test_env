#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>

/* Raw little-endian halfwords let an ordinary RISC-V GCC assemble the
 * experimental encodings. t0=x5 is rd and t1=x6 is rs1. Mixing compressed,
 * standard and 48-bit instructions also checks instruction-length decoding. */
#define EMIT48(value) \
    ".2byte ((" value ") & 65535), (((" value ") >> 16) & 65535), (((" value ") >> 32) & 65535)\n"
#define K_OP(name, encoding) \
    static uintptr_t name(uintptr_t input) { \
        uintptr_t result; \
        __asm__ volatile("mv t1, %1\n" \
                         ".2byte 0x0001\n" /* c.nop */ \
                         EMIT48(encoding) \
                         ".4byte 0x00000013\n" /* nop */ \
                         "mv %0, t0\n" \
                         : "=r"(result) : "r"(input) : "t0", "t1"); \
        return result; \
    }

K_OP(lli, "(0x89abcdef << 12) | (5 << 7) | 0x5f")
K_OP(add_negative, "(1 << 44) | (0xffffff << 20) | (6 << 15) | (5 << 7) | 0x5f")
K_OP(add_minimum, "(1 << 44) | (0x800000 << 20) | (6 << 15) | (5 << 7) | 0x5f")
K_OP(add_maximum, "(1 << 44) | (0x7fffff << 20) | (6 << 15) | (5 << 7) | 0x5f")
K_OP(and_immediate, "(1 << 44) | (0xabcdef << 20) | (6 << 15) | (1 << 12) | (5 << 7) | 0x5f")

static int zero_register(void) {
    uintptr_t result;
    __asm__ volatile(EMIT48("(0xffffffff << 12) | 0x5f")
                     EMIT48("(1 << 44) | (1 << 20) | (6 << 15) | 0x5f")
                     EMIT48("(1 << 44) | (0xffffff << 20) | (6 << 15) | (1 << 12) | 0x5f")
                     "mv %0, zero\n" : "=r"(result) : : "t1");
    return result == 0;
}

#define CHECK(expression, expected) do { \
    uintptr_t actual = (expression), wanted = (expected); \
    if (actual != wanted) { \
        printf("%s: got 0x%" PRIxPTR ", expected 0x%" PRIxPTR "\n", \
               #expression, actual, wanted); \
        ok = 0; \
    } \
} while (0)

int main(void) {
    int ok = 1;
    CHECK(lli(0), (uintptr_t)UINT32_C(0x89abcdef));
    CHECK(add_negative(0), UINTPTR_MAX);
    CHECK(add_negative(42), 41);
    CHECK(add_minimum(0), (uintptr_t)(intptr_t)-8388608);
    CHECK(add_maximum(UINTPTR_MAX), 8388606);
    CHECK(and_immediate(UINTPTR_MAX), 0xabcdef);
    CHECK(and_immediate(0x12345678), (0x12345678 & 0xabcdef));
    CHECK(zero_register(), 1);
#if UINTPTR_MAX > UINT32_MAX
    CHECK(add_negative(UINT64_C(0x1234567800000000)), UINT64_C(0x12345677ffffffff));
    CHECK(and_immediate(UINT64_C(0xffffffff00000000)), 0);
#endif
    puts(ok ? "48-bit regression: PASS" : "48-bit regression: FAIL");
    return ok ? 0 : 1;
}
