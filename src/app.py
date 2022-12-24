from flask import Flask, request
from routes.s2sRoute import s2sRoute
from urllib.parse import parse_qs
from libs.slack2scan import S2S
from threading import Thread

app = Flask(__name__)

app.debug = False

# Routes to the html files
app.register_blueprint(s2sRoute, url_prefix='/cybsec')

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8000)