#
import socketserver


#
from libs.rpc.rpc_s import RPCHost


#
import config


###
### 导入核心API。
###
import apis
apis_name_map = [
        (apis.add_project, "add_project"),
        (apis.add_object, "add_object"),
        (apis.add_task, "add_task"),
        (apis.list_projects, "list_projects"),
        (apis.list_objects, "list_objects"),
        (apis.list_tasks, "list_tasks"),
    ]


###
### 创建rpc主持，注册核心API。
###
rpch = RPCHost()
for nmap in apis_name_map:
    rpch.reg(nmap[0], nmap[1])


#
class RPCRequestHandler(socketserver.StreamRequestHandler):

    #
    def handle(self):
        rpch.handle(self.rfile, self.wfile)


#
def start_server():
    RPC_SERVER_NET_ADDR = config.config["RPC_SERVER_NET_ADDR"]
    RPC_SERVER_TCP_PORT = int(config.config["RPC_SERVER_TCP_PORT"])
    rpc_server = socketserver.ThreadingTCPServer((RPC_SERVER_NET_ADDR, RPC_SERVER_TCP_PORT), RPCRequestHandler)
    rpc_server.serve_forever()
