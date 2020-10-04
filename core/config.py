#
config = {}


#
cmdl_config_ordered_list = []


#
def apply_cmdl_config(args):
    if not len(args) == len(cmdl_config_ordered_list):
        raise ValueError("配置参数数目(" + str(len(args)) + ")不正确。")
    for i in range(len(args)):
        name = cmdl_config_ordered_list[i]
        config[name] = args[i]
