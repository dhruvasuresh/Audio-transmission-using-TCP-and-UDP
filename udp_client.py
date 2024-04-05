import socket
import pyaudio
import threading

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Socket settings
UDP_IP = "0.0.0.0"  # Listen on all IP addresses
UDP_PORT_DATA = 12345  # The port that the server is broadcasting to
UDP_PORT_CONTROL = 12346  # The port that the server is listening for commands on

sock_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_data.bind((UDP_IP, UDP_PORT_DATA))

sock_control = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

client_ip = socket.gethostbyname(socket.gethostname())
print(f"* playing on {client_ip}")

addr = None  # Define addr as a global variable

def handle_data():
    global addr  # Declare addr as global in this function
    while True:
        data, addr = sock_data.recvfrom(CHUNK*2)  # buffer size is 1024 bytes
        stream.write(data)

def handle_input():
    while True:
        user_input = input()
        if user_input.lower() == 'exit':
            sock_control.sendto(user_input.encode('utf-8'), (addr[0], UDP_PORT_CONTROL))
            print("Connection closed")
            break

data_thread = threading.Thread(target=handle_data)
input_thread = threading.Thread(target=handle_input)

data_thread.start()
input_thread.start()

input_thread.join()
data_thread.join()

print("* done playing on", client_ip)

stream.stop_stream()
stream.close()
p.terminate()