# -*- coding: utf-8 -*-
import os
from werkzeug.debug import DebuggedApplication
from flask import Flask
from rq_dashboard import RQDashboard

name = "stock"
app = Flask(name)
RQDashboard(app)

if os.getenv('FLASK_CONF') == 'DEV':
    # Development settings
    app.config.from_object('stock.settings.Development')

elif os.getenv('FLASK_CONF') == 'TEST':
    app.config.from_object('stock.settings.Testing')

else:
    app.config.from_object('stock.settings.Production')

# Enable jinja2 loop controls extension
app.jinja_env.add_extension('jinja2.ext.loopcontrols')


# def make_celery(app):
#     celery = Celery(app.import_name,
#                     broker=app.config['CELERY_BROKER_URL'],
#                     backend=app.config['CELERY_RESULT_BACKEND'])
#     celery.conf.update(app.config)
#     TaskBase = celery.Task
#     class ContextTask(TaskBase):
#         abstract = True
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return TaskBase.__call__(self, *args, **kwargs)
#     celery.Task = ContextTask
#     return celery


# celery = make_celery(app)

import views
