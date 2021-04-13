import os
import re

from django import forms
from django.conf import settings
from django.forms import ModelForm
from .models import Documento, TYPES


class DocumentoForm(ModelForm):

    tipo = forms.ChoiceField(choices=TYPES, required=True)

    class Media:
        js = ('js/validation.js',)

    class Meta:
        model = Documento
        fields = ['nome', 'email', 'tipo', 'arquivo']

    def clean_arquivo(self):
        files = self.files.getlist('arquivo')
        tipo = self.cleaned_data.get('tipo')
        for file in files:
            extension = os.path.splitext(file.name)[1]
            if extension != '.txt' and extension != '.pdf':
                self.add_error('arquivo',
                               'Extensão %s do arquivo %s inválida. Somente arquivos de textos e PDF '
                               'são permitidos.' % (extension, file.name))

            if tipo == 'keywords' and extension != '.txt':
                self.add_error('arquivo', 'Extensão %s do arquivo %s inválida. Somente arquivos .txt '
                                          'são permitidos para esse tipo de arquivo.' % (extension, file.name))

            return self.cleaned_data.get('arquivo')


class LayoutForm(forms.Form):
    imagem = forms.FileField(widget=forms.FileInput(
        attrs=(
            {'class': 'custom-file-input', 'id': 'inputGroupFile01', 'aria-describedby': 'inputGroupFileAddon01'}
        )), label='Imagem:', required=False)
    descricao = forms.CharField(widget=forms.Textarea(),
                                label='Descrição:', required=False)
    stopwords = forms.CharField(widget=forms.Textarea(),
                                label='Adicione mais stopwords (separando-as por ","):', required=False)
    cores = forms.BooleanField(widget=forms.CheckboxInput,
                               label='Cores da Imagem', required=False)