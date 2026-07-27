# Android Reverse Engineering with Frida

Frida hooks and a small Python solver created while analyzing OWASP Android
security-training applications.

## Context

Two independent targets are represented in this directory:

- OWASP UnCrackable Mobile App Level 3, which combines Java and native checks,
  root and debugger detection, anti-instrumentation behavior, and an
  XOR-protected secret phrase;
- RootBeer, an Android root-detection library with multiple independent checks.

The files contain only the analysis helpers. APKs, native libraries, and Frida
binaries are not included.

## Files

### `solve_phrase.py`

Reconstructs the secret phrase checked by the native library in UnCrackable
Level 3.

The analysis of `libfoo.so` showed that:

- the secret is stored as six 32-bit integers;
- the integers are interpreted as little-endian bytes;
- each byte is XORed with a repeating `pizza` key;
- the resulting 24 bytes form the expected UTF-8 phrase.

The script uses only Python's standard `struct` module:

```bash
python solve_phrase.py
```

It prints the recovered phrase to standard output.

### `bypass_root.js`

A Frida script for the protection mechanisms encountered in UnCrackable
Level 3.

Native hook:

- attaches to `strstr` exported by `libc.so`;
- inspects both string arguments for `frida` or `xposed`;
- replaces a matching call's return value with `0`, making the substring appear
  absent.

Java hooks:

- suppress `java.lang.System.exit(int)`;
- force `sg.vantagepoint.util.RootDetection.checkRoot1()` to return `false`;
- force `checkRoot2()` and `checkRoot3()` to return `false`;
- force `android.os.Debug.isDebuggerConnected()` to return `false`.

The script logs successful hooks and most native-hook errors to the Frida
console.

### `bypass_rootbeer.js`

A focused Frida script for the RootBeer library.

It hooks `com.scottyab.rootbeer.RootBeer` and forces these methods to return
`false`:

- `checkForDangerousProps()`;
- `checkForSuBinary()`.

It does not override every check implemented by RootBeer.

## Requirements

- an Android emulator or authorized test device;
- ADB connectivity;
- a compatible `frida-server` running on the device;
- matching Frida tools on the host;
- Python 3 for `solve_phrase.py`.

Install the host-side Frida tools:

```bash
python -m pip install frida-tools
```

## Frida usage

Spawn an authorized target and load the appropriate script:

```bash
frida -U -f <package-name> -l bypass_root.js
```

For the RootBeer target:

```bash
frida -U -f <package-name> -l bypass_rootbeer.js
```

The exact package name depends on the installed training application.

## Safety

Use these scripts only with applications and devices you own or are explicitly
authorized to test. They are intended for mobile application security research
and controlled training environments.

