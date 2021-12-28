import socket
import time
import os
import binascii
import json
import traceback
from threading import *
from Packets.Factory import *
from Logic.Device import Device
from colorama import init, Fore

PORT = 9339

init(True)

class ServerThread():
    def __init__(self, ip, port):
        self.address = str(ip)
        self.port = int(port)
        self.client = socket.socket()

    def start(self):
        print(Fore.GREEN + """   ________           __       ____  _____
  / ____/ /___ ______/ /_     / __ \/ ___/
 / /   / / __ `/ ___/ __ \   / /_/ /\__ \ 
/ /___/ / /_/ (__  ) / / /  / ____/___/ / 
\____/_/\__,_/____/_/ /_/  /_/    /____/  
                                          """)

        self.client.bind((self.address, self.port))

        print(Fore.MAGENTA + "[!] Server is listening on port [" + str(self.port) + "]\n")

        while True:
            self.client.listen(5)
            client, address = self.client.accept()

            print(Fore.CYAN + "[*] New connection from [" + str(address[0]) + "] --> " + Fore.GREEN + "Starting new thread...\n")
            clientThread = ClientThread(client).start()


class ClientThread(Thread):
    def __init__(self, client):
        Thread.__init__(self)

        self.client = client
        self.device = Device(self.client)

    def recvall(self, size):
        data = []
        while size > 0:
            self.client.settimeout(5.0)
            s = self.client.recv(size)
            self.client.settimeout(None)
            if not s:
                raise EOFError
            data.append(s)
            size -= len(s)
        return b''.join(data)

    def run(self):
        while True:
            header   = self.client.recv(7)
            packetID = int.from_bytes(header[:2], 'big')
            length   = int.from_bytes(header[2:5], 'big')
            version  = int.from_bytes(header[5:], 'big')
            data     = self.recvall(length)

            if len(header) >= 7:
                if length == len(data):
                    try:
                        decrypted = self.device.decrypt(data)
                        if packetID in availablePackets:
                            print(Fore.MAGENTA + "[&] Received Packet ID [" + str(packetID) + "] [\"" + availablePackets[packetID] + "\"] --> [HANDLING]")
                            Message = availablePackets[packetID](decrypted, self.device)

                            Message.decode()
                            Message.process()

                        else:
                            print(Fore.RED + "[&] Received Packet ID [" + str(packetID) + "] --> [NOT HANDLING]")

                    except:
                            print(Fore.YELLOW + "[&] Received Packet ID [" + str(packetID) + "] --> [ERROR HANDLING]")
                            traceback.print_exc()
                else:
                    print(Fore.YELLOW + "[&] Incorrect Length for Packet ID [" + str(packetID) + "] [Length: " + str(len(data)) + "] [\"" + data + "\"]")
            else:
                print(Fore.YELLOW + "[&] Received an invalid packet")
                self.client.close()

if __name__ == '__main__':
	server = ServerThread("0.0.0.0", PORT)
	server.start()
