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
def projects():
    method = flask.request.method
    if method == "POST":
        try:
            form = flask.request.form
            assert(type(form["project_name"]) == str)
            r = RPCRemote(CORE_APIS_RPC_ADDR, CORE_APIS_RPC_PORT)
            result = r.pc("add_project")(form["project_name"])
            assert(type(result) == list)
            assert(len(result) == 1)
            assert(type(result[0] == list))
            assert(len(result[0]) == 2)
            if result[0][0] == 0:
                return flask.redirect(flask.url_for("index"))
            else:
                raise RuntimeError("RPC failure:", result[0][0], result[0][1])
        except Exception as e:
            return repr(e)
    else:
        flask.abort(405)


#
route_descs = [
        [projects, [
                ("/projects", ["POST"]),
            ]],
    ]
