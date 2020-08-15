#!/bin/env python2
import zmq, sys, time, argparse, logging, datetime, socket

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)

parser = argparse.ArgumentParser("Simple zmq pubsub example")
parser.add_argument("pub_or_sub", help="Either pub or sub")
parser.add_argument("host", help="host address to connect to if sub otherwise the address to bind to")
parser.add_argument("--port", "-p", type=int, help="The port to use", default=4567)
args = parser.parse_args()

context = zmq.Context()
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if args.pub_or_sub.lower() == "sub":
    tcp_socket.bind((0.0.0.0, args.port+1))
    zmq_socket = context.socket(zmq.SUB)
    zmq_socket.setsockopt(zmq.SUBSCRIBE, "")
    zmq_socket.connect("tcp://{}:{}".format(args.host, args.port))
    while 1:
        if zmq_socket.poll(timeout=1000):
            logging.error("Received: {}".format(zmq_socket.recv()))
        else:
            logging.error("No message available")
elif args.pub_or_sub.lower() == "pub":
    zmq_socket = context.socket(zmq.PUB)
    zmq_socket.bind("tcp://{}:{}".format(args.host, args.port))
    i = 0
    while 1:
        logging.error("Sending message: {}".format(i))
        zmq_socket.send("Message {} at {}".format(i, datetime.datetime.now()))
        i += 1
        time.sleep(1.0)
else:
    raise RuntimeError("Needs to either be sub or pub nothing else allowed")
