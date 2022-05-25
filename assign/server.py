#run: python3 server.py server_port block_duration timeout
#coding: utf-8
#using python3
# run using: python3 client.py IPaddress portofserver
from socket import *
import sys
import time
import threading
from _thread import *
import os

server_port = int(sys.argv[1])
block_duration = int(sys.argv[2])
timeout = int(sys.argv[3])

# list of users currently locked out from logging in
failed = []
# dictionary of all users that have logged in this session : time they logged off
online = {}
# dictionary of usernames currently online : their connectionSocket
socks = {}
# dictionary of lists of people who user has blocked
# blocked[username] = [list of people blocked by username]
blocked = {}

timers = {}



# timer - if this is called, client is told it is inactive and logged out
def user_timer(connectionSocket, username): 
    #if online[username] == 0:
    #    exit()
    if online[username] != 0 and time.time() - online[username] > 1:
        exit()
    i = "inactive".encode('utf-8')
    full = username + " logged out"               
    full = full.encode('utf-8')
    try:
        for s in socks:
            # if a user is blocked, dont send it to them
            if username in blocked[s]:
                continue
            # send message to all users - except sender
            if s != username:
                socks[s].send(full)  
            connectionSocket.send(i)
            connectionSocket.close()
    except OSError:
        exit()
    exit()

serverSocket = socket(AF_INET, SOCK_STREAM)
# creates the server's socket
# AF_INET - underlying network is using IPv4.
# SOCK_STREAM - TCP socket

serverSocket.bind(('localhost', server_port))
#The above line binds (that is, assigns) server_port to the server's socket. 
# In this manner, when anyone sends a packet to port server_port at the IP address of the server 
# (localhost in this case), that packet will be directed to this socket.

serverSocket.listen(1)
#The serverSocket then goes in the listen state to listen for client connection requests. 

# handles all communication with client
def client_thread(connectionSocket):
    # attempt to log user in    
    username = None  
    log_in = False    
    remaining_attempts = 3
    while 1:
        # user first time logging in
        if remaining_attempts == 3:
            lo = "logged_out".encode('utf-8')
            connectionSocket.send(lo)
            # user inputs username and password
            username = connectionSocket.recv(1024).decode()
            password = connectionSocket.recv(1024).decode()       
        # user got password wrong
        else:
            w = "wrong".encode('utf-8')
            connectionSocket.send(w)
            # user only inputs password
            password = connectionSocket.recv(1024).decode()

        # user is timeout out for 3 incorrect passwords as has opened a new terminal
        if username in failed:
            to = "timeout".encode('utf-8')
            connectionSocket.send(to)
            break     
        # user is already online - cant log in again
        try:
            if online[username] == 0:
                to = "alreadyli".encode('utf-8')
                connectionSocket.send(to)
                break  
        except KeyError:
            pass
                     

        # check if credentials are correct     
        with open('credentials.txt') as cred:
            for line in cred:
                auth = line.split()
                if auth[0] == username and auth[1] == password:
                    log_in = True
                    break
        # credentials incorrect
        if log_in == False:
            remaining_attempts = remaining_attempts - 1
            if remaining_attempts == 0:
                to = "timeout".encode('utf-8')
                connectionSocket.send(to)
                failed.append(username)
                time.sleep(block_duration)
                failed.remove(username)
                break
            continue
        # credentials correct - user is logged in
        else:
            li = "logged_in".encode('utf-8')
            connectionSocket.send(li)
            online[username] = 0    
            socks[username] = connectionSocket
            blocked[username] = []

            # send presence notification to all other active users
            presence = username + " logged in"            
            presence = presence.encode('utf-8')
            for s in socks:
                if socks[s] != connectionSocket:
                    socks[s].send(presence)
            break

    # outside the while loop - the user is passed authentication - if they are logged in...
    if log_in == True:
        timers[username] = []               
        while True:
            try:
                u_timer = threading.Timer(timeout, user_timer, args=[connectionSocket, username]) 
                u_timer.start()
                timers[username].append(u_timer)
                fullcommand = connectionSocket.recv(1024).decode()
                for t in timers[username]:
                    t.cancel()

                u_timer = None
                command = fullcommand.split()
                if command:
                    if command[0] == "logout":
                        presence = username + " logged out"            
                        presence = presence.encode('utf-8')
                        for s in socks:
                            if socks[s] != connectionSocket:
                                socks[s].send(presence)
                        break
                    
                    elif command[0] == "whoelse":
                        whoelse = ""
                        for user in online:
                            if user == username:
                                continue
                            if online[user] != 0:
                                continue
                            if whoelse == "":
                                whoelse = user  
                            else:
                                whoelse = whoelse + "\n" + user
                        if whoelse == "":
                            whoelse = "No one else online!"
                        whoelse = whoelse.encode('utf-8')
                        connectionSocket.send(whoelse)

                    elif command[0] == "whoelsesince":
                        # online is a dict: USERNAME:TIMELOGGEDOUT
                        whoelsesince = ""
                        for key in online:
                            # difference in time between now and when user logged out
                            difference = int(time.time()) - int(online[key])
                            # if user is logged in - there is no difference
                            if int(online[key]) == 0:
                                difference = 0     
                            # if difference is greater than command[1] - continue
                            if  difference > int(command[1]):
                                continue
                            # dont include requesting user is list of online people
                            elif key == username:
                                continue
                            # build the whoelsesince string and send it
                            if whoelsesince == "":
                                whoelsesince = key                       
                            else:
                                whoelsesince = whoelsesince + "\n" + key    
                        if whoelsesince == "":
                            whoelsesince = "No one else online!"
                        whoelsesince = whoelsesince.encode('utf-8')
                        connectionSocket.send(whoelsesince)

                    elif command[0] == "broadcast":
                        b = False
                        message = fullcommand[10:]
                        full = username + ": " + message                
                        full = full.encode('utf-8')
                        for s in socks:
                            # if a user is blocked, dont send it to them
                            if username in blocked[s]:
                                b = True
                                #print(s + "is blocked so cant send")
                                continue
                            # send message to all users - except sender
                            if socks[s] != connectionSocket:
                                socks[s].send(full)
                        # if a message could not be sent because user was blocked - tell user
                        if b == True:
                            m = "Your message could not be delivered to some recipients"
                            m = m.encode('utf-8')
                            connectionSocket.send(m)

                    elif command[0] == "message":
                        # sending message to themself
                        if command[1] == username:
                            e = "Error. Cannot message yourself"
                            e = e.encode('utf-8')
                            connectionSocket.send(e)
                            continue
                        # check user the message is being sent to exists
                        real = False
                        with open('credentials.txt') as cred:
                            for line in cred:
                                auth = line.split()
                                if auth[0] == command[1]:
                                    real = True
                                    break
                        if real == False:
                            e = "Error. Invalid user"
                            e = e.encode('utf-8')
                            connectionSocket.send(e)
                            continue
                        # if sender is blocked by receiver - dont send message and let sender know
                        if username in blocked[command[1]]:
                            m = "Your message could not be delivered as the recipient has blocked you"
                            m = m.encode('utf-8')
                            connectionSocket.send(m)
                        # if not - send the message
                        else:
                            message = " ".join(command[2:])   
                            full = username + ": " + message                
                            full = full.encode('utf-8')
                            socks[command[1]].send(full)

                    elif command[0] == "block":
                        # blocking themself
                        if command[1] == username:
                            e = "Error. Cannot block yourself"
                            e = e.encode('utf-8')
                            connectionSocket.send(e)
                            continue
                        # check user being blocked exists
                        real = False
                        with open('credentials.txt') as cred:
                            for line in cred:
                                auth = line.split()
                                if auth[0] == command[1]:
                                    real = True
                                    break
                        if real == False:
                            e = "Error. Invalid user"
                            e = e.encode('utf-8')
                            connectionSocket.send(e)
                            continue
                        # check if user being blocked is already blocked
                        if command[1] in blocked[username]:
                            e = "Error. " + command[1] + " already blocked"
                            e = e.encode('utf-8')
                            connectionSocket.send(e)
                            continue
                        # now block the person
                        else:
                            blocked[username].append(command[1])
                            b = command[1] + " is blocked"
                            b = b.encode('utf-8')
                            connectionSocket.send(b)

                    elif command[0] == "unblock":
                        # blocking themself
                        if command[1] == username:
                            e = "Error. Cannot unblock yourself"
                            e = e.encode('utf-8')
                            connectionSocket.send(e)
                            continue
                        # check user being blocked exists
                        real = False
                        with open('credentials.txt') as cred:
                            for line in cred:
                                auth = line.split()
                                if auth[0] == command[1]:
                                    real = True
                                    break
                        if real == False:
                            e = "Error. Invalid user"
                            e = e.encode('utf-8')
                            connectionSocket.send(e)
                            continue
                        # check if user being unblocked is actually blocked
                        if command[1] not in blocked[username]:
                            e = "Error. " + command[1] + " was not blocked"
                            e = e.encode('utf-8')
                            connectionSocket.send(e)
                            continue
                        # now unblock the person
                        else:
                            blocked[username].remove(command[1])
                            b = command[1] + " is unblocked"
                            b = b.encode('utf-8')
                            connectionSocket.send(b)
                    
                    elif command[0] == "inactive":
                        break                  
                    
                    else:
                        wi = "Error. Invalid command".encode('utf-8')
                        connectionSocket.send(wi)
                else:
                    continue
            except OSError:
                break
        # user is leaving us
        # remove entry for this username
        online[username] = time.time()
        del socks[username]
        connectionSocket.close()

# waits to accept a connection 
# starts a new thread for each connection - calls client_thread to handle connections with clients
while True:   
    connectionSocket, addr = serverSocket.accept()
    #print("[-] Connected to " + addr[0] + ":" + str(addr[1]))
    start_new_thread(client_thread, (connectionSocket,))
try:
    serverSocket.close()
except KeyError:
    exit()

    