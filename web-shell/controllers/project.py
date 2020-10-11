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
def project(project_name:str):
    # 获取project的基本信息。
    try:
        r = RPCRemote(CORE_APIS_RPC_ADDR, CORE_APIS_RPC_PORT)
        result = r.pc("list_projects")()
        assert(type(result) == list)
        assert(len(result) == 1)
        assert(type(result[0] == list))
        assert(len(result[0]) == 2)
        if result[0][0] == 0:
            for project in result[0][1]:
                if project["name"] == project_name:
                    break    # 保留project值。
            else:
                raise RuntimeError("Fetch info failure:", "Project", project_name, "not exists.")
        else:
            raise RuntimeError("RPC failure:", result[0][0], result[0][1])
    except Exception as e:
        return repr(e)
    # 获取project的objects。
    try:
        r = RPCRemote(CORE_APIS_RPC_ADDR, CORE_APIS_RPC_PORT)
        result = r.pc("list_objects")(project_name)
        assert(type(result) == list)
        assert(len(result) == 1)
        assert(type(result[0] == list))
        assert(len(result[0]) == 2)
        if result[0][0] == 0:
            objects = [(object["name"], ) for object in result[0][1]]
        else:
            raise RuntimeError("RPC failure:", result[0][0], result[0][1])
    except Exception as e:
        return repr(e)
    #
    operation_add_object = {
            "url": flask.url_for("objects"),
        }
    #
    args = {
            "project": project,
            "objects": objects,
            "operation_add_object": operation_add_object
        }
    return flask.render_template("project.jinja", args=args)

       
#
route_descs = [
        [project, [
                ("/project/<project_name>", ["GET"]),
            ]],
    ]
