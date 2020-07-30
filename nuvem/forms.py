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
        tipo = self.cleaned_data.get('tipo')
        extension = os.path.splitext(self.cleaned_data.get('arquivo').name)[-1]
        if tipo == 'keywords' and extension != '.txt':
            self.add_error('arquivo', 'Extensão de arquivo inválida. Somente arquivos .txt '
                                      'são permitidos para esse tipo de arquivo.')

        else:
            return self.cleaned_data.get('arquivo')


class LayoutForm(forms.Form):
    imagem = forms.FileField(widget=forms.FileInput(
        attrs=(
            {'class': 'custom-file-input', 'id': 'inputGroupFile01', 'aria-describedby': 'inputGroupFileAddon01'}
        )), label='Imagem:', required=False)
    descricao = forms.CharField(widget=forms.Textarea(), label='Descrição:')
    cores = forms.BooleanField(widget=forms.CheckboxInput, label='Cores da Imagem', required=False)