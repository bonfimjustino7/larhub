import os
from csv import excel

import numpy as np
import json
import urllib

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from wordcloud import WordCloud, STOPWORDS

from .models import Documento
from .forms import DocumentoForm
from PIL import Image
from django.conf import settings
from gerador.genwordcloud import generate
from django.contrib import messages
from django.http import HttpResponseNotFound
import detectlanguage



#testando nova branch
def home(request):
    return render(request, 'home.html')


def nuvem(request):
    documento = Documento.objects.last()
    imagem = generate(documento.arquivo.path)
    
    contexto = {
        'doc': documento,
        'nuvem': imagem
    }
    return render(request, 'nuvem.html', contexto)

def decodificar(arquivo):
    try:
        return arquivo.read().decode('utf8')
    except UnicodeDecodeError:
        return arquivo.read().decode('ISO-8859-1')

def new_doc(request):
    form = DocumentoForm(request.POST or None, request.FILES or None)


    if form.is_valid():
        filename, extencao = os.path.splitext(str(form.cleaned_data['arquivo']))

        ''' Configuration API LANGUAGE DETECT'''
        detectlanguage.configuration.api_key = settings.API_KEY_LANGUAGE

        arquivo = form.cleaned_data['arquivo'].read().decode('ISO-8859-1') #Usei esse decode, pois quando faço um try except p detectlanguage não recebe o texto convertido
        #arquivo = decodificar(form.cleaned_data['arquivo'])
        print(type(arquivo))

        lang_detect = detectlanguage.detect(arquivo)
        print(lang_detect)
        precisao = lang_detect[0]['confidence']


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
            if extencao == '.pdf' or extencao == '.txt':
                post = form.save(commit=False)
                if precisao > 7.5:
                    post.language = lang_detect[0]['language']
                post.save()

                return redirect('nuvem')
            else:
                messages.error(request, 'Extenção do arquivo inválida, por favor selecione um arquivo .txt ou .pdf')
        else:
            messages.error(request, 'ReCAPTCHA inválido. Por favor tente novamente!')

    return render(request, 'person_form.html', {'form': form})
