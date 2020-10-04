#
import flask


#
app = flask.Flask(__name__)


#
from controllers import setup_routes
setup_routes(app)


#
app.run()
