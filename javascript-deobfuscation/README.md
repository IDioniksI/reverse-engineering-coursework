# JavaScript Deobfuscation Utilities

Small Python and JavaScript utilities for unpacking a compressed payload and
recovering strings referenced through an obfuscated JavaScript decoder.

## Context

The files come from two separate reverse-engineering exercises.

The first exercise examined a PDF generated with Metasploit's
`exploit/windows/fileformat/adobe_pdf_embedded_exe` module. An embedded object
was extracted from the PDF as `payload.exe`, but its contents were still a
zlib-compressed stream. `decompress.py` was created to recover the underlying PE
file as `payload_real.exe` for further static analysis.

The second exercise examined an obfuscated `.jse` sample. It contained:

- a large encoded string array named `a`;
- a decoder function named `b`;
- decoder calls in the form `b(index, key)`, with a separate key associated
  with each referenced value.

`gen_js_loop.py` was used to extract those index-and-key pairs and generate
calls that print every decoded value. The encoded array, decoder, and generated
probe calls were then combined in `js_logic.js`.

## Files

### `decompress.py`

Reads a zlib-compressed file named `payload.exe`, decompresses its contents, and
writes the result to `payload_real.exe`.

The script:

- uses Python's standard `zlib` module;
- processes the entire input file as a single zlib stream;
- reports decompression and file-processing errors;
- overwrites `payload_real.exe` if it already exists.

Run it from the directory containing `payload.exe`:

```bash
python decompress.py
```

The script does not validate that the decompressed output is a valid PE
executable.

### `gen_js_loop.py`

Generates JavaScript probe calls for an obfuscated string-decoder function.

The source sample is stored as a string in `malware_js_code`; Python does not
execute that JavaScript. The script:

1. Searches the embedded source for calls matching `b(index, key)`.
2. Removes duplicate index-and-key pairs.
3. Sorts the collected pairs.
4. Generates a `console.log()` call for every unique decoder invocation.
5. Prints the generated JavaScript to standard output.

Run it with:

```bash
python gen_js_loop.py
```

The generated output contains decoder calls only. It must be combined with the
sample's string table and decoder implementation before it can resolve the
strings.

### `js_logic.js`

A prepared string-decoding artifact containing:

- the encoded string array `a`;
- the array-rotation and decoder setup;
- the `b(index, key)` Base64 and RC4-style string-decoder function;
- generated `console.log()` probes for the collected decoder calls.

Executing this file evaluates the decoder calls and prints the recovered
strings. The original downloader body is not included as active top-level logic
in this file.

The original analysis was performed by pasting the prepared code into the
developer console of a blank browser page. A compatible JavaScript runtime may
also be used; for example, if Node.js is available:

```bash
node js_logic.js
```

Review the file before execution and use an isolated analysis environment.

## Workflows

The compressed PDF payload and the `.jse` sample are independent inputs:

```text
PDF embedded object
        |
        v
   payload.exe
  (zlib stream)
        |
        v
  decompress.py
        |
        v
payload_real.exe
   (PE file)

obfuscated .jse sample
        |
        v
 gen_js_loop.py
        |
        v
 decoder probe calls
        |
        v
   js_logic.js
        |
        v
 recovered strings
```

## Requirements

- Python 3 for both Python scripts;
- a browser developer console, Node.js, or another compatible JavaScript
  runtime for `js_logic.js`.

The Python scripts use only the standard library.

## Safety

The embedded source analyzed by `gen_js_loop.py` originated from a downloader
sample and contains network and process-execution indicators as inert text.
The Python generator does not execute it. Treat decompressed files and any
reconstructed JavaScript as untrusted, and analyze them only in an isolated
environment without access to sensitive data.
