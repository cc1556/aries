#
import flask


#
from . import RPCRemote


#
from config import config


#
CORE_APIS_RPC_ADDR = config["CORE_APIS_RPC_ADDR"]
CORE_APIS_RPC_PORT = int(config["CORE_APIS_RPC_PORT"])


#
def index():
    #
    try:
        r = RPCRemote(CORE_APIS_RPC_ADDR, CORE_APIS_RPC_PORT)
        result = r.pc("list_projects")()
        assert(type(result) == list)
        assert(len(result) == 1)
        assert(type(result[0] == list))
        assert(len(result[0]) == 2)
        if result[0][0] == 0:
            projects = [(project["name"], ) for project in result[0][1]]
        else:
            raise RuntimeError("RPC failure:", result[0][0], result[0][1])
    except Exception as e:
        return repr(e)
    #
    operation_add_project = {
            "url": flask.url_for("projects"),
        }
    #
    args = {
            "projects": projects,
            "operation_add_project": operation_add_project
        }
    return flask.render_template("index.jinja", args=args)

       
#
route_descs = [
        [index, [
                ("/", ["GET"]),
                ("/index", ["GET"]),
            ]],
    ]
