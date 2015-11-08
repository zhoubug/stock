from django import forms

class StockSearchForm(forms.Form):
    name = forms.CharField(max_length=50)
