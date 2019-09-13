from django.forms import ModelForm
from .models import Documento


class DocumentoForm(ModelForm):
    class Meta:
        model = Documento
        fields = ['nome', 'email', 'arquivo']
