#!/usr/bin/env python3

import logging
import sys
import time
import socket

HOST = ''   # Symbolic name, meaning all available interfaces
PORT = 8775 # Arbitrary non-privileged port

def main():
    root_logger = logging.getLogger()
    root_logger.setLevel("INFO")
    root_logger.addHandler(SystemdHandler())
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.info('Socket created')

    try:
        s.bind((HOST, PORT))
        logging.info('Socket bind complete')
        s.listen(10)
        logging.info('Socket now listening')
        while 1:
            conn, addr = s.accept()
            logging.info('Connected with ' + addr[0] + ':' + str(addr[1]))
    except socket.error as msg:
        logging.error('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    except KeyboardInterrupt:
        logging.info('Interrupt received, stopping…')
    finally:
        s.close()
        sys.exit()


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
