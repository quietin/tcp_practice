import time
import signal
from datetime import timedelta
from tornado.ioloop import IOLoop
from tornado.tcpserver import TCPServer
from tornado import gen

from lib.util import prefix_to_len

_default_seconds = 3


class EchoServer(TCPServer):
    def __init__(self):
        logger.info('Start listening')
        super(EchoServer, self).__init__()
        self._msg_map = {}
        self._conn_counter = 0
        self.bytes_counter = 0
        self.packet_counter = 0
        self.start_time = time.time()

    @gen.coroutine
    def handle_stream(self, stream, address):
        logger.info("New connection from %s:%s" % address)
        self._conn_counter += 1
        msg_size = yield self._connection_callback(stream, address)
        yield self._message_callback(stream, address, msg_size)
        stream.set_close_callback(self._on_connection_close)

    @gen.coroutine
    def _connection_callback(self, stream, addr):
        raw_size = yield stream.read_bytes(4)
        raise gen.Return(prefix_to_len(raw_size))

    @gen.coroutine
    def _message_callback(self, stream, addr, size):
        def on_message(data):
            if data:
                self.bytes_counter += len(data)
                self.packet_counter += 1
            stream.read_bytes(size, on_message)

        on_message(None)

    def _on_connection_close(self):
        logger.info('One client closed')
        self._conn_counter -= 1

    @staticmethod
    def calculate_speed(self):
        if self._conn_counter:
            elapsed = time.time() - self.start_time
            mb = self.bytes_counter / (elapsed * 1024 * 1024)
            logger.info('Rate: %.3f MB/s, msg: %d/s' %
                        (mb, int(self.packet_counter / elapsed)))

        self.bytes_counter = self.packet_counter = 0
        self.start_time = time.time()
        IOLoop.current().add_timeout(timedelta(seconds=_default_seconds),
                                     self.calculate_speed,
                                     self)


def signal_handler(signum, frame):
    IOLoop.current().add_callback(IOLoop.current().stop)


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)
    server = EchoServer()
    server.listen(8888)
    signal.signal(signal.SIGINT, signal_handler)
    IOLoop.current().add_timeout(timedelta(seconds=_default_seconds),
                                 server.calculate_speed,
                                 server)
    IOLoop.current().start()
    IOLoop.current().close()
