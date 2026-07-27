#!/bin/bash
i686-w64-mingw32-gcc leak.c -o leak.exe
strip -s leak.exe
for i in $(seq -f %03g 0 999); do
    sed "s/KITTY000/KITTY$i/" leak.exe > out/bit.$i.exe
done
