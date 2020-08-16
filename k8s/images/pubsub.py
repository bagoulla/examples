#!/bin/env python2
import zmq, sys, time, argparse, logging, datetime, threading
from zmq.utils.monitor import recv_monitor_message

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)

if zmq.zmq_version_info() < (4, 0):
    raise RuntimeError("monitoring in libzmq version < 4.0 is not supported")

logging.error("libzmq-%s" % zmq.zmq_version())
if zmq.zmq_version_info() < (4, 0):
    raise RuntimeError("monitoring in libzmq version < 4.0 is not supported")

EVENT_MAP = {}
logging.error("Event names:")
for name in dir(zmq):
    if name.startswith('EVENT_'):
        value = getattr(zmq, name)
        logging.error("%21s : %4i" % (name, value))
        EVENT_MAP[value] = name


def event_monitor(monitor):
    while monitor.poll():
        evt = recv_monitor_message(monitor)
        evt.update({'description': EVENT_MAP[evt['event']]})
        logging.error("Event: {}".format(evt))
        if evt['event'] == zmq.EVENT_MONITOR_STOPPED:
            break
    monitor.close()
    logging.error("event monitor thread done!")

parser = argparse.ArgumentParser("Simple zmq pubsub example")
parser.add_argument("pub_or_sub", help="Either pub or sub")
parser.add_argument("host", help="host address to connect to if sub otherwise the address to bind to")
parser.add_argument("--port", "-p", type=int, help="The port to use", default=4567)
args = parser.parse_args()

context = zmq.Context()

if args.pub_or_sub.lower() == "sub":
    zmq_socket = context.socket(zmq.SUB)
    monitor = zmq_socket.get_monitor_socket()
    t = threading.Thread(target=event_monitor, args=(monitor,))
    t.setDaemon(True)
    t.start()

    zmq_socket.setsockopt(zmq.SUBSCRIBE, "")
    zmq_socket.connect("tcp://{}:{}".format(args.host, args.port))
    while 1:
        if zmq_socket.poll(timeout=1000):
            logging.error("Received: {}".format(zmq_socket.recv()))
        else:
            logging.error("No message available")
elif args.pub_or_sub.lower() == "pub":
    zmq_socket = context.socket(zmq.PUB)
    monitor = zmq_socket.get_monitor_socket()
    t = threading.Thread(target=event_monitor, args=(monitor,))
    t.setDaemon(True)
    t.start()
    zmq_socket.bind("tcp://{}:{}".format(args.host, args.port))
    i = 0
    while 1:
        logging.error("Sending message: {}".format(i))
        zmq_socket.send("Message {} at {}".format(i, datetime.datetime.now()))
        i += 1
        time.sleep(1.0)
else:
    raise RuntimeError("Needs to either be sub or pub nothing else allowed")
