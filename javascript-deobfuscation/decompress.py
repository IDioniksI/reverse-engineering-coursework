import zlib
import sys

input_file = "payload.exe"
output_file = "payload_real.exe"

try:
    with open(input_file, 'rb') as f:
        compressed_data = f.read()
    
    decompressed_data = zlib.decompress(compressed_data)

    with open(output_file, 'wb') as f:
        f.write(decompressed_data)
        
    print(f"Файл '{input_file}' успішно розпаковано.")
    print(f"Справжній .exe збережено як: {output_file}")

except zlib.error as e:
    print(f"Не вдалося розпакувати файл: {e}")
except Exception as e:
    print(f"Виникла помилка: {e}")
