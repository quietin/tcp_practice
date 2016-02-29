import signal
import threading
import socket
import sys
import errno
from tornado.util import errno_from_exception
from tool.util import len_to_prefix


class EchoClient:
    port = 8888

    def __init__(self, host, size):
        self.size = size
        self.host = host
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.register_signal_handler()
        self._connected = False

    def msg_loop(self):
        logger.info('Have connected to server %s:%s' % (host, self.port))
        msg = 'H' * size
        self._connected = True
        while self._connected:
            try:
                self.sock.send(msg)
            except socket.error as err:
                eno = errno_from_exception(err)
                if eno in (errno.EWOULDBLOCK, errno.EAGAIN):
                    continue
                elif eno in (errno.EPROTOTYPE, errno.EPIPE):
                    break
                raise

    def notify_size(self):
        self.sock.send(len_to_prefix(self.size))

    def receive(self):
        while True:
            try:
                info = self.sock.recv(4)
                if not info:
                    self.sock.shutdown(socket.SHUT_WR)
                    self._connected = False
                    logger.info('Server closed!')
            except socket.error as err:
                if errno_from_exception(err) in (errno.EWOULDBLOCK, errno.EAGAIN):
                    continue
                raise

    def close(self):
        self._connected = False
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def signal_handler(self, signal, frame):
        logger.info('Ctrl+C - Client exit!')
        self.close()
        sys.exit(0)

    def register_signal_handler(self):
        signal.signal(signal.SIGINT, self.signal_handler)

    def spawn_recv_thread(self):
        recv_thread = threading.Thread(target=self.receive)
        recv_thread.setDaemon(True)
        recv_thread.start()

    def connect(self):
        self.sock.connect((self.host, self.port))
        self.sock.setblocking(0)
        if hasattr(socket, "TCP_NODELAY"):
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self.spawn_recv_thread()
        self.notify_size()
        self.msg_loop()


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)
    # set host, size as sys argv later
    host = '127.0.0.1'
    size = 64
    client = EchoClient(host, size)
    client.connect()
