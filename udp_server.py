import socket
import pyaudio
import threading

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Socket settings
BROADCAST_IP = "10.20.207.255"  # Change this to your network's broadcast address
UDP_PORT_DATA = 12345
UDP_PORT_CONTROL = 12346

sock_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

sock_control = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_control.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock_control.bind(("0.0.0.0", UDP_PORT_CONTROL)) 

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* broadcasting audio on", BROADCAST_IP, ":", UDP_PORT_DATA)   

def broadcast_audio():
    while True:
        data = stream.read(CHUNK)
        sock_data.sendto(data, (BROADCAST_IP, UDP_PORT_DATA))

def listen_for_commands():
    while True:
        command, addr = sock_control.recvfrom(1024)
        if command.decode('utf-8') == 'exit':
            print("* done recording and broadcasting audio on", BROADCAST_IP, ":", UDP_PORT_DATA)
            stream.stop_stream()
            stream.close()
            p.terminate()
            break

# Start the threads
threading.Thread(target=broadcast_audio).start()
threading.Thread(target=listen_for_commands).start()