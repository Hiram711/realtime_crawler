#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'
import click
from flask import Flask
from .uitls import JsonResponse, MyEncoder
from .config import BaseConfig
from .views import main_bp
from .models import db, User
from .caching import cache


def create_app():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)
    app.response_class = JsonResponse
    app.json_encoder = MyEncoder
    db.init_app(app)
    cache.init_app(app)
    app.register_blueprint(main_bp)

    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, User=User, cache=cache)

    @app.cli.command()
    def init():
        """Initialize app."""
        click.echo('Initializing the database...')
        db.drop_all()
        db.create_all()
        User.init_user()

    return app
