# CPUID Hypervisor Detection

Windows C++ examples that use the `CPUID` instruction to detect common
virtualized environments and select a different execution path.

## Shared detection logic

All three files contain the same `IsVirtualMachine()` function:

1. `CPUID` leaf `1` is queried and bit 31 of `ECX` is checked for the
   hypervisor-present flag.
2. Hypervisor leaf `0x40000000` is queried to obtain the vendor identifier.
3. The identifier is compared with a fixed list of known hypervisors:
   KVM, Hyper-V, VMware, Xen, Parallels, and VirtualBox.

The function returns `true` only when the hypervisor-present bit is set and the
reported vendor matches one of the known identifiers.

## Files

### `detect_vm_mes_box.cpp`

A safe demonstration of the detection function.

- When a known hypervisor is detected, the program displays an environment
  detection message.
- Otherwise, it displays `Hello kitty!`.

This example contains no embedded payload and is the recommended starting point
for reviewing the code.

### `detect_vm_calc.cpp`

Extends the same detection logic with an embedded 32-bit Windows shellcode
example.

- When a known hypervisor is detected, the program displays an environment
  detection message and does not execute the shellcode.
- Otherwise, it allocates executable memory, copies the embedded shellcode into
  it, and transfers execution to it.
- The shellcode resolves `WinExec` and opens
  `C:\Windows\System32\calc.exe`.

The shellcode is based on Iliya Dafchev's
[Basics of Windows shellcode writing](https://idafchev.github.io/exploit/2017/09/26/writing_windows_shellcode.html)
example.

This file must be compiled as an **x86 target**. The embedded code uses 32-bit
registers, the 32-bit process environment block layout, and the `FS` segment
register.

### `detect_vm_shellcode.cpp`

An archived prototype that combines hypervisor detection with an AES-encrypted
payload.

As currently written:

- the encrypted byte array, AES key, and IV are stored in the source;
- the AES-CBC decryption branch runs only when a known hypervisor is detected;
- decrypted bytes are copied into executable memory and called directly.

## Building

Use a Visual Studio Developer Command Prompt.

The MessageBox example can be built for x86 or x64:

```bat
cl /EHsc detect_vm_mes_box.cpp user32.lib
```

Build the calculator variant from an x86 developer prompt:

```bat
cl /EHsc detect_vm_calc.cpp user32.lib
```

The AES prototype is intentionally not included in the build instructions.
