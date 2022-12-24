from flask import Blueprint
from controllers.s2sController import scan, download, interactive

s2sRoute = Blueprint('s2sRoute', __name__)

s2sRoute.route('/scan', methods=['POST'])(scan)
s2sRoute.route('/download/<fileId>', methods=['GET'])(download)
s2sRoute.route('/interactive', methods=['POST'])(interactive)