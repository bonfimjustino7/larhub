from django.contrib import admin
from nuvem.models import Documento


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'arquivo', 'pdf_link')
    readonly_fields = ['pdf_link']