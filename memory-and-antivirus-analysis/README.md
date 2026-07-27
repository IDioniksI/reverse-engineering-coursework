# Memory Parsing and Antivirus Oracle Experiments

Windows analysis utilities consisting of a process-memory configuration parser
and several closely related antivirus-oracle prototypes.

## Structure

```text
parser/
└── script.py

getCompName/
getDesktopFiles/
getNotepad/
getProcess/
getUserName/
├── leak.c
├── leak.h
├── gen.sh
├── python_convert.py
└── binary_string.txt
```

The five oracle directories are intentionally self-contained. Their
`leak.h`, `gen.sh`, and `python_convert.py` files are identical; only `leak.c`
and the captured `binary_string.txt` differ.

## Process-memory parser

### `parser/script.py`

A Python 2 and WinAppDbg script that:

- requests debug privileges;
- scans running processes for `client.exe`;
- prints its PID and architecture;
- reads committed memory regions with accessible content;
- searches process memory for IPv4 addresses beginning with `192.`.

The script is intended to recover a locally stored server address from the
running process, including when the executable has been packed but its
configuration is available in unpacked process memory.

Requirements:

- Windows;
- Python 2;
- WinAppDbg;
- sufficient privileges to inspect the target process.

## Antivirus-oracle pipeline

Each oracle variant follows the same general flow:

1. `leak.c` collects target data into a byte buffer.
2. The `KITTY000` marker identifies the bit index to inspect.
3. The selected bit determines which byte array from `leak.h` is decoded.
4. The selected array is XOR-decoded into `malware.exe` and executed.
5. `gen.sh` creates multiple executables by replacing the three-digit marker.
6. External scan results are converted into `binary_string.txt`.
7. `python_convert.py` restores the byte and bit order and prints the recovered
   data.

### `leak.h`

Contains two arrays encoded with XOR `0xFF`:

- `bit1` represents the EICAR antivirus test file;
- `bit0` represents a Windows calculator payload.

The antivirus classification of the generated output acts as the observable
result for the selected source bit.

### `gen.sh`

Cross-compiles `leak.c` as a 32-bit Windows executable using MinGW, strips the
binary, and generates variants named `bit.000.exe` through `bit.999.exe`.

The script expects an existing `out/` directory and the tools
`i686-w64-mingw32-gcc`, `strip`, `sed`, and `seq`.

### `python_convert.py`

Reads `binary_string.txt`, corrects the stored bit and byte order, converts the
result to bytes, removes surrounding null bytes, and prints the recovered
value.

It requires PyCryptodome:

```bash
python -m pip install pycryptodome
```

## Oracle variants

| Directory | Data collected by `leak.c` |
| --- | --- |
| `getCompName` | Computer name returned by `GetComputerNameA()` |
| `getUserName` | Current username returned by `GetUserName()` |
| `gatProcess` | Comma-separated process names from a Tool Help snapshot |
| `getDesktopFiles` | Names found on the current user's desktop |
| `getNotepad` | First 32 bytes of `C:\Windows\System32\notepad.exe` |

`getDesktopFiles` also creates `maomao.txt` on the desktop before enumerating
the directory, ensuring that the collected buffer contains at least one known
filename.

## Current limitations

- Most helper files are exact duplicates across the five directories.
- The empty `report1.txt` files do not contain the external antivirus reports
  used to produce the stored bit strings.
- `parser/script.py` uses Python 2 syntax and a legacy debugging library.
- Results depend on external scanner behavior and are not deterministic across
  antivirus products or signature versions.

## Safety

The oracle samples reconstruct and execute either an EICAR test file or an
embedded calculator payload as `malware.exe`. Generate or run them only inside
an isolated, authorized analysis environment. Do not upload generated samples
to public services or test them on production systems.

