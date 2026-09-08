from django.shortcuts import render
from django.views.generic import TemplateView


class SmartCartAppView(TemplateView):
    """
    Renders the SmartCart React SPA.
    """
    template_name = 'index.html'
