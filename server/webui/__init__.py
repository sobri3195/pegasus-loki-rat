from flask import Blueprint

webui = Blueprint('webui', __name__, template_folder='templates')

from . import routes
