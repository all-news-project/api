import socket

# Resolve the IP address of the Docker host
host_ip = socket.gethostbyname('host.docker.internal')
print("Host IP address:", host_ip)
