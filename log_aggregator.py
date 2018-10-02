"""
It's likely that any large-enough system will run over multiple processes,
and maybe multiple machines on the same subnet. So this is an aggregator
that collects logs from all those places and presents them together. I
haven't yet given thought to how to efficiently store and/or filter those
logs. This thing functions as an HTTP server, and is actually an old piece
of code I had sitting around from when I previously thought about this
same stuff a few years ago.
"""

import pickle
import logging
import logging.handlers
import select
import socket
import SocketServer
import struct

AGGREGATOR_HOST = "localhost"


class LogRecordStreamHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = pickle.loads(chunk)
            record = logging.makeLogRecord(obj)
            client_ip, _ = self.connection.getpeername()
            record.clientname = socket.gethostbyaddr(client_ip)[0]
            self.handleLogRecord(record)

    def handleLogRecord(self, record):
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        logger.handle(record)
        # Alternatively, throw records into a database or into
        # something like Logstash or Loggly or Splunk


class LogRecordSocketReceiver(SocketServer.ThreadingTCPServer):
    allow_reuse_address = 1

    def __init__(self,
                 host=None,
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler):
        if host is None:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((AGGREGATOR_HOST, 0))
            host = s.getsockname()[0]
            s.close()
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    def serve_until_stopped(self):
        abort = 0
        while not abort:
            rd, _, _ = select.select([self.socket.fileno()], [], [],
                                     self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort


def getLogger(
        logname="",      # empty string -> root logger
        aggregator=AGGREGATOR_HOST,
        level=logging.INFO,
        port=logging.handlers.DEFAULT_TCP_LOGGING_PORT  # 9020
        ):
    logger = logging.getLogger(logname)
    logger.setLevel(level)
    socketHandler = logging.handlers.SocketHandler(aggregator, port)
    logger.addHandler(socketHandler)
    return logger


def main():
    logging.basicConfig(
        format='-- %(relativeCreated)5d %(clientname)s:' +
        '%(name)s %(levelname)s %(filename)s:%(lineno)d\n' +
        '%(message)s'
    )
    tcpserver = LogRecordSocketReceiver()
    tcpserver.serve_until_stopped()


if __name__ == '__main__':
    main()
