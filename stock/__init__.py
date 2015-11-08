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

import trading_environment
import views
import jobs
