import sys
from typing import Optional, Tuple, List

CALL_SIG = b"\xE8\xE2\xFF\xFF\xFF"
MAGIC_BYTE = 0x7B  # '{'
TYPICAL_KEY_OFFSET = 0x24

def printable_ratio(b: bytes) -> float:
    """Return ratio of printable/whitespace bytes in b."""
    if not b:
        return 0.0
    good = sum(1 for x in b if 32 <= x <= 126 or x in (9,10,13))
    return good / len(b)

def find_magic_and_table(payload: bytes, magic: int = MAGIC_BYTE) -> Optional[Tuple[int,int]]:
    """Find magic byte and the encoded-data start after a zero-terminated table.

    Returns (magic_index, encoded_data_start) or None.
    """
    try:
        mi = payload.index(magic)
    except ValueError:
        return None
    tstart = mi + 1
    tend = tstart
    while tend < len(payload) and payload[tend] != 0:
        tend += 1
    encoded_start = tend + 1
    return mi, encoded_start

def detect_decoder_key_size(payload: bytes) -> Optional[int]:
    """Try to detect decoder key size n in the first 0x40 bytes:
    look for a byte b such that b+5 also appears in that region and 1 <= b <= 40."""
    header = payload[:0x40]
    for b in header:
        if ((b + 5) & 0xFF) in header:
            if 1 <= b <= 40:
                return b
    return None

def decode_with_key(payload: bytes, key: bytes, encoded_start: int) -> bytes:
    """Decode payload bytes starting at encoded_start by subtracting key cyclically."""
    if len(key) == 0:
        return payload[encoded_start:]
    out = bytearray()
    for i, v in enumerate(payload[encoded_start:]):
        kv = key[i % len(key)]
        out.append((v - kv) & 0xFF)
    return bytes(out)

def try_forced_key(payload: bytes, encoded_start: int, offset: int = TYPICAL_KEY_OFFSET, n: int = 18) -> Tuple[bytes, float, bytes]:
    """Force-try a key located at offset with length n. Returns (decoded, score, key)."""
    if offset + n > len(payload):
        return b'', 0.0, b''
    key = payload[offset:offset+n]
    dec = decode_with_key(payload, key, encoded_start)
    score = printable_ratio(dec)
    return dec, score, key

def call_sig_transform(payload: bytes) -> Optional[bytes]:
    """If CALL_SIG is found, extract following data and apply simple static transforms:
    replace 0x00 -> 'A' and 0x05 -> 'B' (observed behavior in some decoders)."""
    idx = payload.find(CALL_SIG)
    if idx == -1:
        return None
    data_start = idx + len(CALL_SIG)  # dynamic hook would compute address + i.address + 5 (5 == len sig)
    data = bytearray(payload[data_start:])
    # according to observed behavior, dynamic code performed simple replacements 0x00 -> 'A', 0x05 -> 'B'
    data = data.replace(b'\x00', b'A').replace(b'\x05', b'B')
    return bytes(data)

def brute_force_key_search(payload: bytes, encoded_start: int, offsets_range: Tuple[int,int]=(0x18, 0x30), max_n: int=40):
    """Brute-force search keys across offsets_range and lengths up to max_n.
    Returns best tuple (score, offset, n, key, decoded) or None."""
    best = None  # (score, offset, n, key, decoded)
    for offset in range(offsets_range[0], offsets_range[1]):
        max_possible = min(max_n, len(payload)-offset)
        if max_possible <= 0:
            continue
        for n in range(1, max_possible+1):
            key = payload[offset:offset+n]
            dec = decode_with_key(payload, key, encoded_start)
            score = printable_ratio(dec)
            # small bonus for ASCII in prefix to prefer readable starts
            prefix = dec[:8]
            if len(prefix) > 0:
                ascii_prefix = sum(1 for c in prefix if 32 <= c <= 126) / float(len(prefix))
            else:
                ascii_prefix = 0.0
            score += 0.05 * ascii_prefix
            if best is None or score > best[0]:
                best = (score, offset, n, key, dec)
    return best

def main(fname: str):
    with open(fname, "rb") as f:
        payload = f.read()

    # 1) find the start of encoded data via magic byte and zero-terminated table
    tab = find_magic_and_table(payload)
    if tab is None:
        print("Magic byte not found (0x7B); will try other approaches.")
        # try call_sig_transform as a fallback
        transformed = call_sig_transform(payload)
        if transformed:
            print("CALL_SIG transform found. Preview:")
            print(repr(transformed[:200]))
            open("static_decoded_output.bin","wb").write(transformed)
            print("Saved static_decoded_output.bin")
            return
        else:
            print("No magic byte and no CALL_SIG found. Please paste hexdump of the first ~96 bytes.")
            return
    magic_index, encoded_start = tab
    print(f"Magic byte found at index {magic_index}")
    print(f"Assuming encoded data starts at {encoded_start}")

    # 2) auto-detect decoder_key_size
    detected = detect_decoder_key_size(payload)
    if detected:
        print(f"Auto-detected decoder_key_size = {detected}")
        forced_n = detected
        forced_offset = TYPICAL_KEY_OFFSET
        if forced_offset + forced_n <= len(payload):
            key = payload[forced_offset:forced_offset+forced_n]
            dec = decode_with_key(payload, key, encoded_start)
            score = printable_ratio(dec)
            print(f"Try offset 0x{forced_offset:02X}, n={forced_n}, printable_ratio={score:.3f}")
            if score > 0.4:
                print("--- decoded preview ---")
                print(dec[:400].decode(errors='replace'))
                open("decoded.bin","wb").write(dec)
                print("Saved decoded.bin")
                return
    else:
        print("Auto-detect failed; will try fallback and brute force.")

    # 3) fallback n=18 @0x24 (common for msfvenom)
    dec, score, key = try_forced_key(payload, encoded_start, TYPICAL_KEY_OFFSET, 18)
    print(f"Fallback try offset 0x{TYPICAL_KEY_OFFSET:02X}, n=18, printable_ratio={score:.3f}, key={list(key)}")
    if score > 0.4:
        print("--- decoded preview ---")
        print(dec[:400].decode(errors='replace'))
        open("decoded.bin","wb").write(dec)
        print("Saved decoded.bin")
        return

    # 4) if nothing else worked — try to find CALL_SIG and transform
    transformed = call_sig_transform(payload)
    if transformed:
        print("Found CALL_SIG and applied transforms. Preview:")
        print(repr(transformed[:400]))
        try:
            print(transformed.decode('utf-8', errors='replace')[:400])
        except:
            pass
        open("static_decoded_output.bin","wb").write(transformed)
        print("Saved static_decoded_output.bin")
        return

    # 5) last resort — brute force offsets/lengths
    print("Doing brute-force search around offsets 0x18..0x2F and n up to 40 (fast).")
    best = brute_force_key_search(payload, encoded_start, (0x18, 0x30), 40)
    if best:
        score, offset, n, key, dec = best
        print(f"Chosen decoder_key_size = {n} at offset 0x{offset:02X} (score={score:.3f})")
        print(f"Extracted key (len {len(key)}): {list(key)}")
        print("--- preview decoded (first 400 chars) ---")
        print(dec[:400].decode(errors='replace'))
        open("decoded.bin","wb").write(dec)
        print("Saved decoded.bin")
        return

    print("Automatic recognition failed. If you want, I can port the nonupper.rb from Metasploit 1:1 into Python (gen_decoder + encode_byte).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python nonupper_port.py payload.bin")
        sys.exit(1)
    main(sys.argv[1])
