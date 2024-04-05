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
host_ip = '10.20.202.8'

data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data_socket.connect((host_ip, data_port))

# Wrap the data_socket with SSL context
data_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
data_context.check_hostname = False
data_context.verify_mode = ssl.CERT_NONE
data_context.load_cert_chain(certfile=r"d:\Users\Dhruva\Desktop\CN project\client.crt", keyfile=r"d:\Users\Dhruva\Desktop\CN project\client.key")
data_socket = data_context.wrap_socket(data_socket, server_side=False, server_hostname=host_ip)

control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket.connect((host_ip, control_port))

# Wrap the control_socket with SSL context
control_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
control_context.check_hostname = False
control_context.verify_mode = ssl.CERT_NONE
control_context.load_cert_chain(certfile=r"d:\Users\Dhruva\Desktop\CN project\client.crt", keyfile=r"d:\Users\Dhruva\Desktop\CN project\client.key")
control_socket = control_context.wrap_socket(control_socket, server_side=False, server_hostname=host_ip)

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

def receive_data():
    while True:
        packed_msg_size = data_socket.recv(8)
        if not packed_msg_size:
            break
        msg_size = struct.unpack("Q", packed_msg_size)[0]
        data = b""
        while len(data) < msg_size:
            packet = data_socket.recv(msg_size - len(data))
            if not packet:
                break
            data += packet
        stream.write(data)

def send_control_command(command):
    control_socket.sendall(command)
    print("Sent control command:", command)

receive_thread = threading.Thread(target=receive_data)
receive_thread.start()

while True:
    command = input("Enter control command (type 'exit' to quit): ")
    if command == 'exit':
        break
    send_control_command(command.encode())

stream.stop_stream()
stream.close()
p.terminate()
data_socket.close()
control_socket.close()