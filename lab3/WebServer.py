import socket
import sys
import os.path
from os import path
from datetime import date

# create socket
socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = int(sys.argv[1])
socket1.bind(('localhost', port))

socket1.listen(1)

while True:
    connection, client_address = socket1.accept()
    data = connection.recv(1024).decode('utf-8')
    x = data.split(' ')
    if len(x) < 2:
        continue
    y = '.' + x[1]
    if os.path.isfile(y):
        z = x[1].split('.')
        # html - sent as html
        if z[1] == "html":
            fd = open(y, "r")
            
            # send it
            connection.send(
                "HTTP/1.1 200 OK\r\n" + 
                "Date: Sun, 26 Sep 2010 20:09:20 GMT\r\n" +
                "Server: LocalHost\r\n" +
                "Content-Type: text/html\r\n" + 
                "\r\n" +
                fd.read() + "\n\r")
        else:
            # assume everything else is a png
            fd = open(y, "r")
            
            # send it
            connection.send(
                "HTTP/1.1 200 OK\r\n" + 
                "Date: Sun, 26 Sep 2010 20:09:20 GMT\r\n" +
                "Server: LocalHost\r\n" +
                "Content-Type: image/png\r\n" + 
                "\r\n" +
                fd.read() + "\n\r")

    else: 
        #send 404
        connection.send(
            "HTTP/1.1 404 NOT FOUND\r\n" + 
            "Date: Sun, 26 Sep 2010 20:09:20 GMT\r\n" +
            "Server: LocalHost\r\n" +
            "Content-Type: text/html\r\n" + 
            "\r\n" "<p>404 ERROR</p>" + "\n\r")

    connection.close()