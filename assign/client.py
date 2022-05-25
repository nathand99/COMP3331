#coding: utf-8
#using python3
from socket import *
import sys
import threading
from _thread import *
import os

# we have been told that client will be run on the same machine as server - so it always connects to localhost
serverName = 'localhost'
close = False

#change this port number if required
server_IP = str(sys.argv[1])
server_port = int(sys.argv[2])

clientSocket = socket(AF_INET, SOCK_STREAM)
#This line creates the client's socket
#AF_INET - network is using IPv4. 
#SOCK_STREAM - TCP socket

clientSocket.connect((serverName, server_port))
# The above line initiates the TCP connection between the client and server. 
# The parameter of the connect( ) method is the address of the server side of the connection. 
logged_in = False
while 1:
    state = clientSocket.recv(1024)
    # user is logging in for the first time
    if state.decode() == "logged_out":           
        print("Please enter your credentials")
        username = input("Username: ")
        u = username.encode('utf-8')
        clientSocket.send(u)

        password = input("Password: ")
        p = password.encode('utf-8')
        clientSocket.send(p)
    # user is re-entering password because it was incorrect
    elif state.decode() == "wrong":
        print("Invalid Password. Please try again")
        password = input("Password: ")
        p = password.encode('utf-8')
        clientSocket.send(p)

    # user has been blocked because of 3 login failures
    elif state.decode() == "timeout":
        print("Your account is blocked due to multiple login failures. Please try again later")
        break

     # user is already logged in
    elif state.decode() == "alreadyli":
        print("Your account is already logged in - login failed")
        break

    # user is now logged in
    elif state.decode() == "logged_in":
        logged_in = True
        print("Welcome, you are now logged in")
        break

def receive_and_print(clientSocket):
    while True:
        response = clientSocket.recv(1024).decode()
         # user has been inactive
        if response == "inactive":
            print("Inactivity - logging out")    
            send_back = "inactive"
            send_back = send_back.encode('utf-8')
            clientSocket.send(send_back)
            clientSocket.close()
            close = True
            os._exit(os.EX_OK)
            exit()
            
        else:
            print(response)  
# the program continues in a while (input) sending off user commands
# make a new thread that accepts stuff from server and prints it
# at this point the user is passed authentication - if they are logged in....
if logged_in == True:
    start_new_thread(receive_and_print, (clientSocket,))
    while True:
        if close == True:
            break
        command = input()
        clientSocket.send(command.encode('utf-8'))     
        if command == "logout":
            clientSocket.close()
            exit()
            

clientSocket.close()
#and close the socket
