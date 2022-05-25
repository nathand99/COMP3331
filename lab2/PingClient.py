import socket
from datetime import datetime
import time
#import socket.timeout as TimeoutException

message = str.encode("this is a message")
server = ("127.0.0.1", 2019)
bufferSize = 1024

# create socket
socket1 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# set timeout of 1 second
socket1.settimeout(1)
rttlist = []
i = 0
while i < 10: 
    initial_time = time.time() 
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    message = "PING {} {} \r\n".format(i, current_time)
    socket1.sendto(message, server)
    rtt = 0
    try:
        reply = socket1.recvfrom(bufferSize)
        ending_time = time.time()
        rtt = int((ending_time - initial_time) * 1000)
        rttlist.append(rtt)
        msg = "ping to 127.0.0.1, seq = {}, rtt = {} ms".format(i, rtt)
        print(msg)
        i += 1
    except socket.timeout:
        rtt = "time out"
        msg = "ping to 127.0.0.1, seq = {}, {}".format(i, rtt)
        print(msg)
        i += 1
    continue

print("min rtt: {}".format(min(rttlist)))
print("max rtt: {}".format(max(rttlist)))
print("avg rtt: {}".format(sum(rttlist)/len(rttlist)))
