from django.conf import settings
from django.views.generic import TemplateView, FormView
from forms import StockSearchForm
import pandas as pd
import tushare as ts
import os
import datetime

base_dir = os.path.join(settings.STATIC_ROOT, 'data')

class IndexView(TemplateView):
    template_name = 'index.html'

class BasicsView(TemplateView):
    template_name = 'basics.html'
    f = os.path.join(base_dir, 'basics.h5')
    basics = pd.read_hdf(f, 'basics')

    def get_context_data(self, **kwargs):
        context = super(BasicsView, self).get_context_data(**kwargs)
        context['basics'] = self.basics
        return context

class StockSearchView(FormView):
    form = StockSearchForm
    template_name = 'searh.html'
    def form_valid(self, form):
        pass
