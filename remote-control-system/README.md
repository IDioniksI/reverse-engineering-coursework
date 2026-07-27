# Python Remote Control Prototype

A small cross-platform remote control prototype implemented with Python TCP
sockets. It consists of an endpoint that exposes a numbered command interface
and an interactive controller that connects to it.

> The filenames are historical: `client.py` acts as the listening endpoint,
> while `server.py` acts as the controller that initiates the connection.

## Files

### `client.py`

The controlled endpoint. It listens on `0.0.0.0:9999`, accepts one connection at
a time, and dispatches commands received from the controller.

Implemented functions:

- `start_keylogger()` — records keyboard input until a stop command is received;
- `take_screenshot()` — captures the desktop and saves a temporary PNG file;
- `get_system_info()` — returns operating-system and processor information;
- `send_file()` — transfers a file using a simple size-and-data protocol;
- `execute_command()` — executes a shell command and returns its output;
- `list_directory()` — lists files and directories in the current path;
- `handle_file_operation()` — changes directory, downloads, or deletes a file;
- `search_file()` — recursively searches for a filename;
- `get_running_processes()` — returns process information through `psutil`;
- `get_clipboard_content()` — reads the current clipboard value;
- `record_video()` — records webcam video to an AVI file;
- `record_audio()` — records microphone input to a WAV file;
- `handle_client()` — maps numeric commands to the corresponding operations;
- `main()` — creates the listening socket and accepts controller connections.

### `server.py`

The interactive controller. It connects to the endpoint configured in
`main()` and presents a numbered command menu.

Implemented functions:

- `start_keylogger()` — starts and stops remote keyboard capture and stores the
  received log in `keylog.txt`;
- `save_file()` — receives a size-prefixed file and writes it locally;
- `interactive_shell()` — provides an interactive remote command prompt;
- `list_dir()` and `open_dir()` — browse the endpoint filesystem;
- `download_file()` and `delete_file()` — request remote file operations;
- `search_file()` — searches for a file on the endpoint;
- `get_processes()` — displays the remote process list;
- `main()` — establishes the connection and handles the command menu.

## Commands

| Number | Operation | Result |
| ---: | --- | --- |
| 1 | Screenshot | Saves `received_screenshot.png` |
| 2 | System information | Prints OS and processor information |
| 3 | List directory | Prints the current remote directory |
| 4 | Open directory | Changes the current remote path |
| 5 | Download file | Saves the selected file locally |
| 6 | Delete file | Deletes the selected remote file |
| 7 | Command shell | Opens an interactive remote shell |
| 8 | Search file | Searches the remote filesystem |
| 9 | Running processes | Prints PID, process name, and user |
| 10 | Keylogger | Saves captured input to `keylog.txt` |
| 11 | Exit | Closes the controller connection |
| 12 | Clipboard | Prints the current clipboard contents |
| 13 | Video recording | Saves `received_video.avi` |
| 14 | Audio recording | Saves `received_audio.wav` |

## Requirements

- Python 3.8 or later;
- Pillow;
- psutil;
- pynput;
- pyperclip;
- OpenCV;
- sounddevice.

Install the Python dependencies:

```bash
python -m pip install pillow psutil pynput pyperclip opencv-python sounddevice
```

Some capture functions require a graphical desktop, camera, microphone, and the
corresponding operating-system permissions.

## Configuration and execution

Set the endpoint address in `server.py`:

```python
client.connect(("192.168.1.10", 9999))
```

Start the listening endpoint:

```bash
python client.py
```

Then start the controller from another authorized machine:

```bash
python server.py
```

Both machines must be able to reach TCP port `9999`.

## Safety

This prototype exposes shell access, file operations, keyboard capture,
clipboard access, and audio/video recording. Use it only on systems you own or
have explicit permission to test, preferably inside an isolated laboratory
network. It is not suitable for deployment on an untrusted or public network.

