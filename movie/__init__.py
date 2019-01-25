from flask import Flask,render_template
from movie.home import home as home_blueprint
from movie.admin import admin as admin_blueprint
def create_app():
    app = Flask(__name__)
    app.debug=True
    app.register_blueprint(home_blueprint)
    app.register_blueprint(admin_blueprint,url_prefix='/admin')

    @app.errorhandler(404)
    def page_not_found(error):
        """
        404
        """
        return render_template("home/404.html"), 404
    return app
