import socket
import threading

PORT = 5000
TIMEOUT = 600

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.connections = []


    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(TIMEOUT)
            threading.Thread(target = self.listenToClient, args = (client,address)).start()
            self.connections.append(client)


    def listenToClient(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    # Set the response to echo back the recieved data 
                    response = data
                    client.send(response)
                else:
                    raise InterruptedError('Client disconnected')
            except:
                client.close()
                return False

if __name__ == "__main__":
    ThreadedServer('',PORT).listen()