import os
from django.db import models
from django.conf import settings


class Documento(models.Model):
    nome = models.CharField('Nome do pesquisador', max_length=60)
    email = models.EmailField(max_length=50)
    arquivo = models.FileField(upload_to='usuario_pdf', null=True, blank=True)

    @property
    def texto(self):
        filename = os.path.splitext(os.path.basename(self.arquivo.path))[0]
        return os.path.join(settings.MEDIA_URL, 'usuario_pdf', filename+'.txt')

    @property
    def csv(self):
        filename = os.path.splitext(os.path.basename(self.arquivo.path))[0]
        return os.path.join(settings.MEDIA_URL, 'usuario_pdf', filename+'.csv')