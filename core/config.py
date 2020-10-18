#
config = {}


#
cmdl_config_ordered_list = [
        "RPC_SERVER_NET_ADDR",
        "RPC_SERVER_TCP_PORT",
        "GLOBAL_FLOCKS_DIR_PATH",
        "APIS_DATABASE_PATH",
        "APIS_GIT_DIR_PATH",
        "APIS_GIT_HOOKS_PATH",
    ]


#
def apply_cmdl_config(args):
    if not len(args) == len(cmdl_config_ordered_list):
        raise ValueError("配置参数数目(" + str(len(args)) + ")不正确。")
    for i in range(len(args)):
        name = cmdl_config_ordered_list[i]
        config[name] = args[i]
