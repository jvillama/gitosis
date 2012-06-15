import zmq
import sys, os, ConfigParser

config = ConfigParser.ConfigParser()
configfile = os.path.join('/etc/gitosis/config')
config.readfp(open(configfile))
socket_location = config.get('Gitosis Config', 'socket')

context = zmq.Context()
print "Connecting to server..."
socket = context.socket(zmq.REQ)
socket.connect (socket_location)

def test():
    #  Do 10 requests, waiting each time for a response
    for request in range (1,10):
        print "Sending request ", request,"..."
        socket.send ("Hello")
        #  Get the reply.
        message = socket.recv()
        print "Received reply ", request, "[", message, "]"

def notify(reponame):
    print "Sending request for repo '"+reponame+"' to build server"
    socket.send(reponame)
    # Get the reply.
    message = socket.recv()
    print "Received reply [", message, "]"
