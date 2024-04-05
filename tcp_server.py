import socket
import ssl
import pyaudio
import struct
import threading

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Socket settings
data_port = 4982
control_port = 4983
host_ip = '10.20.202.129'

data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data_socket.bind((host_ip, data_port))
data_socket.listen(5)

# Wrap the data_socket with SSL context
data_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
data_context.load_cert_chain(certfile=r"d:\Users\Dhruva\Desktop\CN project\server.crt", keyfile=r"d:\Users\Dhruva\Desktop\CN project\server.key")

control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket.bind((host_ip, control_port))
control_socket.listen(5)

# Wrap the control_socket with SSL context
control_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
control_context.load_cert_chain(certfile=r"d:\Users\Dhruva\Desktop\CN project\server.crt", keyfile=r"d:\Users\Dhruva\Desktop\CN project\server.key")

print('STARTING SERVER AT', host_ip)

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

def handle_client_data(client_socket):
    try:
        while True:
            data = stream.read(CHUNK)
            client_socket.sendall(struct.pack("Q", len(data)) + data)
    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

def handle_control_commands(client_socket):
    while True:
        command = client_socket.recv(CHUNK)
        if not command:
            break
        print("Received control command:", command)

def start_server():
    while True:
        client_data_socket, _ = data_socket.accept()
        client_data_socket = data_context.wrap_socket(client_data_socket, server_side=True)
        client_control_socket, _ = control_socket.accept()
        client_control_socket = control_context.wrap_socket(client_control_socket, server_side=True)
        print('GOT CONNECTION')

        data_thread = threading.Thread(target=handle_client_data, args=(client_data_socket,))
        control_thread = threading.Thread(target=handle_control_commands, args=(client_control_socket,))

        data_thread.start()
        control_thread.start()

start_server()

stream.stop_stream()
stream.close()
p.terminate()