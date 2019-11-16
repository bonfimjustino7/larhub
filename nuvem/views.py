import io
import os
import json
import urllib
import codecs

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView

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
    recaptcha = getattr(settings, "GOOGLE_RECAPTCHA_PUBLIC_KEY", None)

    if form.is_valid():
        filename, extensao = os.path.splitext(str(form.cleaned_data['arquivo']))
        if recaptcha:
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
            result = result['success']
        else:
            result = True

        if result:
            if extensao == '.pdf' or extensao == '.txt':
                post = form.save(commit=False)

                if len(request.FILES.getlist('arquivo')) > 1:
                    doc_extra = []
                    for f in request.FILES.getlist('arquivo'):
                        doc = Documento.objects.create(nome=post.nome, email=post.email, arquivo=f) #implementar a condição aqui se é pdf
                        prefix, file_extension = os.path.splitext(doc.arquivo.path)
                        if file_extension.lower() == '.pdf':
                            pdfparser(doc.arquivo.path)
                            nome_arquivo = prefix + '.txt'
                            doc_extra.append(open(nome_arquivo).read())
                        else:
                            doc_extra.append(open(doc.arquivo.path).read())
                    doc_inteiro = ''
                    for d in doc_extra:
                        doc_inteiro += d
                    object = io.BytesIO(doc_inteiro.encode('utf-8'))
                    dir = os.path.join(settings.MEDIA_URL, 'usuario_pdf')
                    doc_extra = Documento.objects.create(nome=post.nome, email=post.email, arquivo=InMemoryUploadedFile(object, 'teste.txt', 'extra.txt', dir, object.getbuffer(), None))

                    return redirect('nuvem', doc_extra.pk)
                else:
                    post.save()
                    return redirect('nuvem', post.pk)
            else:
                messages.error(request, 'Extensão do arquivo inválida, por favor selecione um arquivo .txt ou .pdf')
        else:
            messages.error(request, 'ReCAPTCHA inválido. Por favor tente novamente!')

    return render(request, 'person_form.html', {'form': form, 'recaptcha': recaptcha})
