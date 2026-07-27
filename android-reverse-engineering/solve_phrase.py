import struct

encrypted_ints = [
    0x1311081d,
    0x1549170f,
    0x1903000d,
    0x15131d5a,
    0x5a0e08,
    0x14130817
]

key = b"pizzapizzapizzapizzapizz"

encrypted_bytes = struct.pack('<6I', *encrypted_ints)

decrypted_flag_bytes = bytearray()

for i in range(len(encrypted_bytes)):
    decrypted_byte = encrypted_bytes[i] ^ key[i]
    decrypted_flag_bytes.append(decrypted_byte)

print("Sec. phrase:")
print(decrypted_flag_bytes.decode('utf-8'))