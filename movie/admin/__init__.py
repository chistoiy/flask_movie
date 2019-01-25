from flask import Blueprint
admin = Blueprint('admin',__name__)

from movie.admin import views