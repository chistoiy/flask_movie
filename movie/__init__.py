from flask import Flask,render_template

import os
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from .models import  *
def create_app():
    app = Flask(__name__)
    app.debug=True

    from movie.home import home as home_blueprint
    from movie.admin import admin as admin_blueprint
    app.register_blueprint(home_blueprint)
    app.register_blueprint(admin_blueprint,url_prefix='/admin')


    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:chis1chang@127.0.0.1:3306/movie1?charset=utf8"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SQLALCHEMY_POOL_SIZE'] = 10
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 5
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
    db.init_app(app)
    app.config['SECRET_KEY'] = '123456'

    app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static","uploads")

    @app.errorhandler(404)
    def page_not_found(error):
        """
        404
        """
        return render_template("home/404.html"), 404

    return app
