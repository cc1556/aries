#
config = {}


#
cmdl_config_ordered_list = [
        "WEB_SERVER_LOCAL_ADDR",
        "WEB_SERVER_LOCAL_PORT",
        "CORE_APIS_RPC_ADDR",
        "CORE_APIS_RPC_PORT",
    ]


#
def apply_cmdl_config(args):
    if not len(args) == len(cmdl_config_ordered_list):
        raise ValueError("配置参数数目(" + str(len(args)) + ")不正确。")
    for i in range(len(args)):
        name = cmdl_config_ordered_list[i]
        config[name] = args[i]
