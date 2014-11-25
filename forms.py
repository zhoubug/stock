from flask_wtf import Form
from wtforms import validators, DateField, SelectField, StringField, TextAreaField
from model import Market
from strategy import strategies

class AnalyseForm(Form):
    start = DateField("start", validators=[validators.input_required()])
    end = DateField("end", validators=[validators.input_required()])
    symbols = StringField("symbols", validators=[validators.input_required()])
    strategy = SelectField("strategy", choices=[(k, k) for k in strategies.keys()],
                           validators=[validators.input_required()])
    parameters = TextAreaField("parameters")
    type = SelectField("type", choices=[("event", "event"), ("return", "return")])
    
