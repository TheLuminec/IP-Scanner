import socket

sock = socket.socket(socket.AF_INET)
print(sock.connect(("8.8.8.8", 443)))