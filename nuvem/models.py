import os
import glob
from django.db import models
from django.conf import settings
from django.utils.html import mark_safe
from django.dispatch import receiver
from django.db.models.signals import *

TYPES = [
    ('simple_text', 'Texto Simples'),
    ('keywords', 'Palavras Chaves'),
]


class Documento(models.Model):
    nome = models.CharField('Nome do pesquisador', max_length=60)
    email = models.EmailField(max_length=50)
    arquivo = models.FileField('Arquivo em PDF ou Texto', upload_to='output', max_length=200)
    language = models.CharField('Linguagem', max_length=5, null=True, blank=True)
    tipo = models.CharField(max_length=12, choices=TYPES, null=True, blank=True)
    imagem = models.ImageField('Imagem Modelo', upload_to='modelo', max_length=200, null=True, blank=True)
    descritivo = models.TextField('Descritivo da Nuvem', null=True, blank=True)
    stopwords = models.TextField('Stopwords Extras', null=True, blank=True)
    chave = models.CharField('Chave de Acesso', max_length=20, null=True, blank=True)
    cores = models.BooleanField(default=False)

    @property
    def texto(self):
        filename = os.path.splitext(os.path.basename(self.arquivo.path))[0]
        return os.path.join(settings.MEDIA_URL, 'output', filename+'.dedup')

    @property
    def csv(self):
        filename = os.path.splitext(os.path.basename(self.arquivo.path))[0]
        return os.path.join(settings.MEDIA_URL, 'output', filename + '.csv')

    @property
    def img(self):
        filename = os.path.splitext(os.path.basename(self.arquivo.path))[0]
        return os.path.join(settings.MEDIA_URL, 'output', filename + '.png')

    def pdf_link(self):
        return mark_safe('<a class="grp-button" href="/nuvem/nuvem/%s?chave=%s">Gerar Nuvem</a>' % (self.id, self.chave))

    pdf_link.short_description = 'Nuvem'


@receiver(post_delete, sender=Documento)
def deletar_arquivos(sender, instance, **kwargs):
    prefix = os.path.splitext(instance.arquivo.path)[0]
    for filePath in glob.glob(prefix + '.*'):
        os.remove(filePath)
