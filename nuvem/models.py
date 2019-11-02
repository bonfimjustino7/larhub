import os
from django.db import models
from django.conf import settings
from django.utils.html import mark_safe
from django.dispatch import receiver
from django.db.models.signals import *

class Documento(models.Model):
    nome = models.CharField('Nome do pesquisador', max_length=60)
    email = models.EmailField(max_length=50)
    arquivo = models.FileField('Arquivo em PDF ou Texto',upload_to='usuario_pdf', max_length=200)
    language = models.CharField('Linguagem', max_length=5, null=True, blank=True)
    titulo = models.TextField('Título do artigo/livro', null=True, blank=True)

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

@receiver(post_delete, sender=Documento)
def deletar_arquivos(sender, instance, **kwargs):
    print(instance.arquivo.path)
    os.remove(instance.arquivo.path)