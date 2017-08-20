from flask import Flask, render_template, request, g

from config import config

from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


toolbar = DebugToolbarExtension()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    toolbar.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    
    from .employee import employee as employee_blueprint
    app.register_blueprint(employee_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .manager import manager as manager_blueprint
    app.register_blueprint(manager_blueprint, url_prefix='/manager')


    @app.before_request
    def active_dropdownnav():
        g.app_name = app.config['APP_NAME']

        try:
            g.dropdownnav = request.path.rstrip('/').split('/')[1]
        except IndexError:
            g.dropdownnav = 'default'
        
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403


    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404


    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    
    return app
