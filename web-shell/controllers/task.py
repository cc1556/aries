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
def task(project_name:str, object_name:str, task_name:str):
    # 获取task的基本信息。
    try:
        r = RPCRemote(CORE_APIS_RPC_ADDR, CORE_APIS_RPC_PORT)
        result = r.pc("list_tasks")(object_name, project_name)
        assert(type(result) == list)
        assert(len(result) == 1)
        assert(type(result[0] == list))
        assert(len(result[0]) == 2)
        if result[0][0] == 0:
            for task in result[0][1]:
                if task["name"] == task_name:
                    break    # 保留task值。
            else:
                raise RuntimeError("Fetch info failure:", "In project", project_name, ", in object", object_name, "task", task_name, "not exists.")
        else:
            raise RuntimeError("RPC failure:", result[0][0], result[0][1])
    except Exception as e:
        return repr(e)
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
    #
    args = {
            "task": task,
            "object": object,
            "project": project,
        }
    return flask.render_template("task.jinja", args=args)

       
#
route_descs = [
        [task, [
                ("/task/<project_name>/<object_name>/<task_name>", ["GET"]),
            ]],
    ]
