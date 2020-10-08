#
import flask


#
from tcp_rpc_c import TCPRPCRemote as RPCRemote


###
### 在此添加待注册路由。
###
route_descs = []


#
def setup_routes(app:flask.Flask):
    for rd in route_descs:
        view = rd[0]
        for url in rd[1]:
            app.add_url_rule(view, url)
