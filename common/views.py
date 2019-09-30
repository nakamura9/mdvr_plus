from django.shortcuts import render, reverse
from django.views.generic import TemplateView, UpdateView
import os 
from reports.models import Vehicle
from common.models import Config
from common.forms import ConfigForm
from common.mixins import ContextMixin
from django.http import HttpResponse
from reports.daily_reports import (generate_daily_harsh_braking_summary,
                                  generate_daily_speeding_report)

class Home(TemplateView):
    template_name = os.path.join('common', 'home.html')

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context.update({
            'vehicles': Vehicle.objects.all()
        })
        return context


class EmptyPage(TemplateView):
    template_name = os.path.join('common', 'empty_page.html')


class ConfigFormView(ContextMixin, UpdateView):
    context = {
        'title': 'Configure Email service'
    }
    queryset = Config.objects.all()
    form_class = ConfigForm
    template_name = os.path.join('common', 'create.html')
    success_url = '/app/'


def daily(request):
    generate_daily_harsh_braking_summary()
    return HttpResponse('Done')