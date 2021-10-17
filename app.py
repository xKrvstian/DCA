from flask import Flask
from dca.api_routes import api
from dca.config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(api, url_prefix="/api")

if __name__ == '__main__':
	app.run()
