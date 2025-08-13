# core/views.py

from django.views.generic import TemplateView


class HomePageView(TemplateView):
    """
    Renderiza la página de inicio estática del proyecto.
    """
    template_name = "homepage.html"
