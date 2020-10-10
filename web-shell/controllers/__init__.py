#
import flask


#
from tcp_rpc_c import TCPRPCRemote as RPCRemote


###
### 在此添加待注册路由。
###
route_descs = []
from .index import route_descs as route_descs_i
route_descs.extend(route_descs_i)
from .project import route_descs as route_descs_i
route_descs.extend(route_descs_i)
from .projects import route_descs as route_descs_i
route_descs.extend(route_descs_i)
from .object import route_descs as route_descs_i
route_descs.extend(route_descs_i)
from .objects import route_descs as route_descs_i
route_descs.extend(route_descs_i)
from .tasks import route_descs as route_descs_i
route_descs.extend(route_descs_i)


#
def setup_routes(app:flask.Flask):
    for rd in route_descs:
        view = rd[0]
        for url, methods in rd[1]:
            app.add_url_rule(url, view_func=view, methods=methods)
