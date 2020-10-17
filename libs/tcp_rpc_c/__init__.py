#
import socket


#
from .libs.rpc.rpc_c import RPCRemote


#
class TCPRPCRemote(RPCRemote):


    #
    def _clear_old_socket(self):
        self.rfile.close()
        self.rfile = None
        self.wfile.close()
        self.wfile = None
        self.socket.close()
        self.socket = None


    #
    def _adapt_new_socket(self):
        self.socket_is_connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rfile = self.socket.makefile("rb", buffering=0)
        self.wfile = self.socket.makefile("wb", buffering=0)


    #
    def _connect_socket(self):
        self.socket.connect((self.addr, self.port))
        self.socket_is_connected = True
    

    #
    def __init__(self, addr, port, retry=3):
        #
        self.addr = addr
        self.port = port
        self.retry = retry
        #
        self._adapt_new_socket()
        #
        self.rpc = self.pc
    

    #
    def _pc(self, proc_name:str, *args):
        if not self.socket_is_connected:
            self._connect_socket()
        exc = None
        for _ in range(self.retry):
            try:
                r = super(TCPRPCRemote, self)._pc(proc_name, *args)
                break
            except BrokenPipeError as e:
                exc = e    # ?
                self._clear_old_socket()
                self._adapt_new_socket()
                self._connect_socket()
                continue
        else:
            raise exc
        return r
