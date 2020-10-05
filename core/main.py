#
import sys


#
import config


###
### 传递命令行参数。
###
cmdl_config = sys.argv[1:]
config.apply_cmdl_config(cmdl_config)


###
### 启动rpc服务器。
###
import rpc
rpcs = rpc.start_server()
