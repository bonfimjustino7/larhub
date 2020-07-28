import os
import re

from django import forms
from django.conf import settings
from django.forms import ModelForm
from .models import Documento, TYPES


class DocumentoForm(ModelForm):

    tipo = forms.ChoiceField(choices=TYPES, required=True)

    class Meta:
        model = Documento
        fields = ['nome', 'email', 'tipo', 'arquivo']
