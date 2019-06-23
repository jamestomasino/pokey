#!/usr/bin/env python3

import logging
import sys
import time
import socket
import select
import queue as Queue

PORT = 8775 # Arbitrary non-privileged port

def main():
    # Init logger
    root_logger = logging.getLogger()
    root_logger.setLevel("INFO")
    root_logger.addHandler(SystemdHandler())

    # create async socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)

    try:
        server.bind(('localhost', PORT))
        server.listen(5)
        inputs = [server]
        outputs = []
        message_queues = {}
    except socket.error as msg:
        logging.error('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])

    while inputs:
        readable, writable, exceptional = select.select(
            inputs, outputs, inputs)
        for s in readable:
            if s is server:
                connection, client_address = s.accept()
                connection.setblocking(0)
                inputs.append(connection)
                message_queues[connection] = Queue.Queue()
            else:
                data = s.recv(1024)
                if data:
                    message_queues[s].put(data)
                    if s not in outputs:
                        outputs.append(s)
                else:
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                    del message_queues[s]

        for s in writable:
            try:
                next_msg = message_queues[s].get_nowait()
            except Queue.Empty:
                outputs.remove(s)
            else:
                s.send(next_msg)

        for s in exceptional:
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()
            del message_queues[s]


class SystemdHandler(logging.Handler):
    PREFIX = {
        #logging.EMERG: "<0>",
        #logging.ALERT: "<1>",
        logging.CRITICAL: "<2>",
        logging.ERROR: "<3>",
        logging.WARNING: "<4>",
        #logging.NOTICE: "<5>",
        logging.INFO: "<6>",
        logging.DEBUG: "<7>",
        logging.NOTSET: "<7>"
    }

    def __init__(self, stream=sys.stdout):
        self.stream = stream
        logging.Handler.__init__(self)

    def emit(self, record):
        try:
            msg = self.PREFIX[record.levelno] + self.format(record)
            msg = msg.replace("\n", "\\n")
            self.stream.write(msg + "\n")
            self.stream.flush()
        except Exception:
            self.handleError(record)


if __name__ == '__main__':
    main()
