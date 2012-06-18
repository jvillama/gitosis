import zmq
import sys, os, ConfigParser

config = ConfigParser.ConfigParser()
configfile = os.path.join('/etc/gitosis/config')
config.readfp(open(configfile))
socket_location = config.get('Gitosis Config', 'socket')

context = zmq.Context()
print "Connecting to server..."
socket = context.socket(zmq.REQ)
socket.setsockopt(zmq.LINGER, 0)
socket.connect(socket_location)

# use poll for timeouts:
poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)
timeout = 3*1000 # 3s timeout in milliseconds

def polltest():
    #socket.send_json({"msg": "testmsg"}) # send can block on other socket types, so keep track
    socket.send("Hello")
   
    if poller.poll(timeout):
        #msg = socket.recv_json()
        message = socket.recv()
        print "Received reply [", message, "]"
    else:
        #raise IOError("Timeout processing auth request")
        print "Couldn't Connect to Server, please try again"

    # these are not necessary, but still good practice:
    #socket.close()
    #context.term()

    #sys.exit(0)

def test():
    #  Do 10 requests, waiting each time for a response
    for request in range(1,10):
        print "Sending request ", request,"..."
        socket.send("Hello")
        #  Get the reply.
        if poller.poll(timeout):
            message = socket.recv()
            print "Received reply ", request, "[", message, "]"
        else:
            print "Couldn't Connect to Server, please try again"

def notify(reponame):
    print "Sending request for repo '"+reponame+"' to build server"
    socket.send(reponame)

    if poller.poll(timeout):
        # Get the reply
        message = socket.recv()
        print "Received reply [", message, "]"
    else:
        print "Couldn't Connect to Server, please try again"

