import os

from flask import Flask, redirect, url_for

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()



def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('flask.cfg')
    app.jinja_env.globals.update(zip=zip)

    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)

    from project import models

    @app.route('/')
    def hello():
        #return 'Hello, World!'
        return redirect(url_for('timer.timer'))


    from project import timer
    app.register_blueprint(timer.bp)


    app.add_url_rule('/', endpoint='index')

    return app
