from django.contrib import admin
from nuvem.models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('nome', 'idade', 'pdf',)