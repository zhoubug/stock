from flask_wtf import Form
from wtforms import validators, DateField, SelectField, SelectMultipleField
from model import Market
from strategy import strategies

class AnalyseForm(Form):
    start = DateField("start", validators=[validators.input_required()])
    end = DateField("end", validators=[validators.input_required()])
    symbols = SelectMultipleField("symbols", choices=[(s, s) for s in Market.get_symbol_list()],
                                  validators=[validators.input_required()])
    strategy = SelectField("strategy", choices=[(k, k) for k in strategies],
                           validators=[validators.input_required()])
