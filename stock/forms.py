from flask_wtf import Form
from wtforms import validators
from wtforms import DateField, SelectField, StringField, TextAreaField, SelectMultipleField
from model import Market
from strategy import strategies
from analyse import ANALYSTS

class AnalyseForm(Form):
    start = DateField("start", validators=[validators.input_required()])
    end = DateField("end", validators=[validators.input_required()])
    symbols = StringField("symbols",
                          validators=[validators.input_required()])
    parameters = TextAreaField("parameters")
