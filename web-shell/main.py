#
import sys


#
import config


###
### 传递命令行参数。
###
cmdl_config = sys.argv[1:]
config.apply_cmdl_config(cmdl_config)


#
import flask


#
app = flask.Flask(__name__)


#
from controllers import setup_routes
setup_routes(app)


#
app.run()
