import zmq
import sys, os, ConfigParser

class BuildHook(object):
    def __init__(self):
        self.config = None
        self.socket_location = None
        self.timeout = None

    def parse_config(self):
        config = ConfigParser.ConfigParser()
        configfile = os.path.join('/etc/gitosis/config')
        config.readfp(open(configfile))
        self.config = config

    def connect(self):
        """Connect to the socket"""
        self.socket_location = self.config.get('Gitosis Config', 'socket')

        context = zmq.Context()
        print "Connecting to server..."
        self.socket = context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.connect(self.socket_location)

        # use poll for timeouts:
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        # timeout in milliseconds
        self.timeout = self.config.get('Gitosis Config', 'timeout')

    def pollmsg(self):
        #socket.send_json({"msg": "testmsg"}) # send can block on other socket types, so keep track
        print "Sending Hello request ..."
        self.socket.send("Hello")
    
        if self.poller.poll(self.timeout):
            #msg = socket.recv_json()
            message = self.socket.recv()
            print "Received reply [", message, "]"
        else:
            #raise IOError("Timeout processing auth request")
            print "Couldn't Connect to Server, please try again"

        # these are not necessary, but still good practice:
        #socket.close()
        #context.term()

        #sys.exit(0)

    def sockettest(self):
        #  Do 10 requests, waiting each time for a response
        for request in range(1,10):
            print "Sending request ", request,"..."
            self.socket.send("Hello")
            #  Get the reply.
            if self.poller.poll(self.timeout):
                message = socket.recv()
                print "Received reply ", request, "[", message, "]"
            else:
                print "Couldn't Connect to Server, please try again"

    def notify(self, reponame):
        print "Sending request for repo '"+reponame+"' to build server"
        self.socket.send(reponame)

        if self.poller.poll(self.timeout):
            # Get the reply
            message = socket.recv()
            print "Received reply [", message, "]"
        else:
            print "Couldn't Connect to Server, please try again"

def polltest():
    """High level pollmsg test"""
    hook = BuildHook()
    hook.parse_config()
    hook.connect()
    hook.pollmsg()

def notify(repository_name):
    """High level notify api"""
    hook = BuildHook()
    hook.parse_config()
    hook.connect()
    hook.notify(repository_name)
    
