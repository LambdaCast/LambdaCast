from django.contrib import admin
from pages.models import Page

class PageAdmin(admin.ModelAdmin):
    list_display = ['title','description','activated']
    ordering = ['-title']
admin.site.register(Page,PageAdmin)
