# Static and Dynamic Deobfuscation

This directory contains two experimental approaches to decoding payloads produced
by a Metasploit `x86/nonupper`-style encoder. The project was originally created
as coursework for a reverse engineering and malware analysis class.

The goal is to demonstrate how the same encoded data can be approached from two
different directions:

- **Static deobfuscation** reconstructs the decoder parameters directly from the
  input bytes without executing them.
- **Dynamic deobfuscation** emulates the decoder and observes its behavior through
  instruction hooks.

## Static deobfuscation

[`static_deobfuscation.py`](static_deobfuscation.py) analyzes a binary payload
without executing it. It attempts to:

1. Locate the marker and zero-terminated table preceding the encoded data.
2. Infer the decoder key size from the payload header.
3. Extract a cyclic key from the expected decoder-stub area.
4. Decode the remaining bytes by subtracting the corresponding key bytes.
5. Fall back to known offsets, a decoder signature, or a small heuristic search
   when automatic detection fails.

Candidate results are ranked using a simple printable-byte ratio. This makes the
tool useful for the sample it was designed around, but it is not intended to be
a general-purpose Metasploit decoder.

### Usage

The static script uses only the Python standard library:

```bash
python static_deobfuscation.py payload.bin
```

Depending on the path taken during analysis, the decoded data is written to:

- `decoded.bin`; or
- `static_decoded_output.bin`.

The script also prints the detected offsets, key information, heuristic score,
and a short preview of the result.

## Dynamic deobfuscation

[`dynamic_deobfuscation.py`](dynamic_deobfuscation.py) loads the same payload
into the [Unicorn Engine](https://www.unicorn-engine.org/), disassembles
instructions with [Capstone](https://www.capstone-engine.org/), and monitors
execution with a code hook. The current implementation configures both engines
for x86-64.

The hook inspects each executed instruction, detects the relevant decoder
signature, reads the transformed data from emulated memory, and stops emulation
when the decoder reaches its breakpoint. This allows the decoder's behavior to
be observed without running the payload directly on the host system.

Install its dependencies with:

```bash
python -m pip install unicorn capstone pwntools
```

Place the input in this directory as `payload.bin`, then run:

```bash
python dynamic_deobfuscation.py
```

The dynamic script prints the executed instructions and transformed data to the
terminal. It does not create an output file.

## Comparison

| Approach | Advantages | Limitations |
| --- | --- | --- |
| Static | Does not execute the input; easy to inspect and reproduce | Relies on recognizable layout, constants, and heuristics |
| Dynamic | Observes the decoder as it runs; less dependent on reconstructing every operation manually | Requires a correctly configured emulator and safe memory/register setup |

## Scope and limitations

- The implementation is tailored to one encoder family and a specific coursework
  sample.
- Several constants, including offsets and signatures, are sample-specific.
- The readability score is only a heuristic; binary output may be valid even when
  its score is low.
- No payload samples are included in this repository.
- The tools should be used only with files that you own or are authorized to
  analyze.

## Educational purpose

This project is intended for defensive security research, reverse engineering
practice, and demonstrating static-analysis and emulation techniques in an
isolated laboratory environment.
