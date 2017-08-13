from flask import Blueprint

manager = Blueprint('manager', __name__, template_folder='../templates/manager')

from . import views
