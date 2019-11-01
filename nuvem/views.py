import os
import json
import urllib
import codecs

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Documento
from .forms import DocumentoForm
from PIL import Image
from django.conf import settings
from gerador.genwordcloud import generate
from django.contrib import messages
from django.http import HttpResponseNotFound
import detectlanguage
from gerador.pdf2txt import pdfparser

''' Configuration API LANGUAGE DETECT'''
detectlanguage.configuration.api_key = settings.API_KEY_LANGUAGE


# testando nova branch
def home(request):
    return render(request, 'home.html')


def nuvem(request, id):
    documento = Documento.objects.get(pk=id)

    nome_arquivo = documento.arquivo.path
    prefix, file_extension = os.path.splitext(nome_arquivo)
    if file_extension.lower() == '.pdf':
        pdfparser(documento.arquivo.path)
        nome_arquivo = prefix+'.txt'

    if not documento.language:
        try:
            linhas = open(nome_arquivo).read().lower().split('\n')[0:20]
        except UnicodeDecodeError as erro:
            linhas = open(nome_arquivo, encoding='ISO-8859-1').read().lower().split('.')[0:20]
        trecho = ' '.join([('' if len(linha) < 20 else linha) for linha in linhas])
        lang_detect = detectlanguage.detect(trecho)
        precisao = lang_detect[0]['confidence']
        if precisao > 7:
            documento.language = lang_detect[0]['language']
            documento.save()

    imagem = generate(nome_arquivo, documento.language)

    contexto = {
        'doc': documento,
        'nuvem': imagem
    }
    return render(request, 'nuvem.html', contexto)


def new_doc(request):
    form = DocumentoForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        filename, extensao = os.path.splitext(str(form.cleaned_data['arquivo']))

        ''' Begin reCAPTCHA validation '''
        recaptcha_response = request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        ''' End reCAPTCHA validation '''

        if result['success']:
            if extensao == '.pdf' or extensao == '.txt':
                post = form.save(commit=False)
                post.save()
                return redirect('nuvem', id=post.pk)
            else:
                messages.error(request, 'Extensão do arquivo inválida, por favor selecione um arquivo .txt ou .pdf')
        else:
            messages.error(request, 'ReCAPTCHA inválido. Por favor tente novamente!')

    return render(request, 'person_form.html', {'form': form})
