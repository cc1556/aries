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
def object(project_name:str, object_name:str):
    # 获取object的基本信息。
    try:
        r = RPCRemote(CORE_APIS_RPC_ADDR, CORE_APIS_RPC_PORT)
        result = r.pc("list_objects")(project_name)
        assert(type(result) == list)
        assert(len(result) == 1)
        assert(type(result[0] == list))
        assert(len(result[0]) == 2)
        if result[0][0] == 0:
            for object in result[0][1]:
                if object["name"] == object_name:
                    break    # 保留object值。
            else:
                raise RuntimeError("Fetch info failure:", "In project", project_name, ", object", object_name, "not exists.")
        else:
            raise RuntimeError("RPC failure:", result[0][0], result[0][1])
    except Exception as e:
        return repr(e)
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
    # 获取object的tasks。
    try:
        r = RPCRemote(CORE_APIS_RPC_ADDR, CORE_APIS_RPC_PORT)
        result = r.pc("list_tasks")(object_name, project_name)
        assert(type(result) == list)
        assert(len(result) == 1)
        assert(type(result[0] == list))
        assert(len(result[0]) == 2)
        if result[0][0] == 0:
            tasks = [(task["name"], ) for task in result[0][1]]
        else:
            raise RuntimeError("RPC failure:", result[0][0], result[0][1])
    except Exception as e:
        return repr(e)
    #
    operation_add_task = {
            "url": flask.url_for("tasks"),
        }
    #
    args = {
            "object": object,
            "project": project,
            "tasks": tasks,
            "operation_add_task": operation_add_task
        }
    return flask.render_template("object.jinja", args=args)

       
#
route_descs = [
        [object, [
                ("/object/<project_name>/<object_name>", ["GET"]),
            ]],
    ]
