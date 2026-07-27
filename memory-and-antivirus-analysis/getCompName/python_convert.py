from Crypto.Util.number import long_to_bytes as l2b


with open("binary_string.txt", "r", encoding="utf-8") as f:
    raw_string = f.read().strip()
binary_string = raw_string[::-1]

padding = len(binary_string) % 8
if padding != 0:
    binary_string = binary_string + '0' * (8 - padding)

chunks = [binary_string[i:i+8] for i in range(0, len(binary_string), 8)]
reversed_chunks = [chunk[::-1] for chunk in chunks]
corrected_binary_string = "".join(reversed_chunks)

binary_data = int(corrected_binary_string, 2)
result_bytes = l2b(binary_data)
final_bytes = result_bytes.strip(b'\x00')

print(final_bytes)
