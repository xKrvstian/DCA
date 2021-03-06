from flask import Flask
from dca.api_routes import api
from dca.config import Config
from dca.front import frontend
import os

app_dir = Config.APP_DIR
template_dir = "%s/views" % app_dir
app = Flask(__name__, template_folder=template_dir)
app.config.from_object(Config)
app.register_blueprint(frontend)
app.register_blueprint(api, url_prefix="/api")

if __name__ == '__main__':
	app.run()
