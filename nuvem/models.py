import os
from django.db import models
from django.conf import settings
from django.utils.html import mark_safe


class Documento(models.Model):
    nome = models.CharField('Nome do pesquisador', max_length=60)
    email = models.EmailField(max_length=50)
    arquivo = models.FileField('Arquivo em PDF ou Texto',upload_to='usuario_pdf')
    language = models.CharField('Linguagem', max_length=5, null=True, blank=True)

    @property
    def texto(self):
        filename = os.path.splitext(os.path.basename(self.arquivo.path))[0]
        return os.path.join(settings.MEDIA_URL, 'usuario_pdf', filename+'.txt')

    @property
    def csv(self):
        filename = os.path.splitext(os.path.basename(self.arquivo.path))[0]
        return os.path.join(settings.MEDIA_URL, 'usuario_pdf', filename+'.csv')

    @property
    def img(self):
        filename = os.path.splitext(os.path.basename(self.arquivo.path))[0]
        return os.path.join(settings.MEDIA_URL, 'usuario_pdf', filename + '.png')

    def pdf_link(self):
        return mark_safe('<a class="grp-button" href="/nuvem/nuvem/%s">Gerar Nuvem</a>' % self.id)
    pdf_link.short_description = 'Nuvem'