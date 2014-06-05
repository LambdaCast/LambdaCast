from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from pages.models import Page

def page(request,slug):
    current_page = get_object_or_404(Page, slug=slug)
    return TemplateResponse(request, 'pages/page.html', {'current_page': current_page})
