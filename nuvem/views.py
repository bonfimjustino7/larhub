import os
import re
import uuid
import json
import urllib
import detectlanguage
import numpy as np
from PIL import Image
from django.http import HttpResponseRedirect

from django.shortcuts import render, redirect, get_object_or_404

from .models import Documento
from .forms import DocumentoForm, LayoutForm
from django.conf import settings
from gerador.genwordcloud import generate, generate_words
from django.contrib import messages
from gerador.pdf2txt import pdf2txt

''' Configuration API LANGUAGE DETECT'''
detectlanguage.configuration.api_key = settings.API_KEY_LANGUAGE


def home(request):
    return render(request, 'home.html')


def custom_redirect(url_name, *args, **kwargs):
    from django.urls import reverse
    url = reverse(url_name, args = args)
    params = urllib.parse.urlencode(kwargs)
    return HttpResponseRedirect(url + "?%s" % params)


def nuvem(request, id):
    documento = Documento.objects.get(pk=id)
    form = LayoutForm(request.POST or None, request.FILES or None, initial={'descricao': documento.descritivo or None})
    flag = documento.chave == request.GET.get('chave')

    if request.POST:
        if form.is_valid():
            documento.descritivo = form.cleaned_data.get('descricao')
            if form.cleaned_data.get('imagem'):
                documento.imagem = form.cleaned_data.get('imagem')
            documento.save()
            messages.success(request, 'Alteração salva com sucesso.')

    nome_arquivo = documento.arquivo.path
    prefix, file_extension = os.path.splitext(nome_arquivo)
    if not os.path.exists(prefix + '.txt'):
        pdf2txt(documento.arquivo.path)

    nome_arquivo = prefix + '.txt'

    if not documento.language:
        try:
            linhas = open(nome_arquivo).read().lower().split('\n')[0:20]
        except UnicodeDecodeError as erro:
            linhas = open(nome_arquivo, encoding='ISO-8859-1').read().lower().split('.')[0:20]
        trecho = ' '.join([('' if len(linha) < 20 else linha) for linha in linhas])
        lang_detect = detectlanguage.detect(trecho)
        if len(lang_detect) > 0:
            precisao = lang_detect[0]['confidence']
            if precisao > 7:
                documento.language = lang_detect[0]['language']
                documento.save()
    mask = None
    if documento.imagem:
        try:
            mask = np.array(Image.open(documento.imagem))
        except Exception:
            mask = None
            messages.error(request, 'Não foi possivel usar a imagem como mascára, por favor selecione outra.')

    if documento.tipo == 'keywords':
        imagem = generate_words(nome_arquivo, documento.language, mask)
    else:
        imagem = generate(nome_arquivo, documento.language, mask)

    contexto = {
        'show': flag,
        'form': form,
        'doc': documento,
        'nuvem': imagem
    }

    return render(request, 'nuvem.html', contexto)


def new_doc(request):
    form = DocumentoForm(request.POST or None, request.FILES or None)
    recaptcha = getattr(settings, "GOOGLE_RECAPTCHA_PUBLIC_KEY", None)

    if form.is_valid():
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
            post = form.save(commit=False)
            key = uuid.uuid4()[:20]
            if request.FILES:
                if post.tipo == 'keywords':
                    filename = os.path.join(settings.MEDIA_ROOT,'output', post.arquivo.name)
                    url_filename = os.path.join('output', post.arquivo.name)
                    with open(filename, 'w') as file_writer:
                        for file in request.FILES.getlist('arquivo'):
                            file_str = file.read().decode()
                            file_str = re.sub(r'[\n]', ',', file_str)
                            file_str = file_str.replace('\r', '')
                            linhas = []
                            for linha in file_str.split(','):
                                linha = linha.strip().capitalize()
                                if len(linha) > 50:
                                    linhas.append(linha.replace(' ', ''))
                                else:
                                    linhas.append(linha)

                            file_str = ','.join(linhas)

                            file_writer.write(file_str)

                    doc = Documento.objects.create(nome=post.nome, email=post.email, arquivo=url_filename,
                                                   tipo=post.tipo, chave=key)

                    return custom_redirect('nuvem', doc.pk, chave=key)
                else:
                    # Verifica se todos os arquivos são PDF ou TXT antes de gravar
                    for f in request.FILES.getlist('arquivo'):
                        filename, extensao = os.path.splitext(str(f))
                        if not (extensao == '.pdf' or extensao == '.txt'):
                            messages.error(request,
                                           'Extensão do arquivo %s inválida. Por favor selecione arquivos .txt ou .pdf' %
                                           filename)
                            return render(request, 'person_form.html', {'form': form, 'recaptcha': recaptcha})

                    docs = []
                    for f in request.FILES.getlist('arquivo'):
                        filename, extensao = os.path.splitext(str(f))
                        doc = Documento.objects.create(nome=post.nome, email=post.email, arquivo=f, tipo=post.tipo,
                                                       chave=key)
                        if extensao == '.pdf':
                            pdf2txt(doc.arquivo.path)
                        docs.append(doc)

                    if len(docs) > 1:
                        extra_filename = str(uuid.uuid4())+'.txt'
                        extra_file = open(os.path.join(settings.MEDIA_ROOT, 'output',extra_filename), 'w+')
                        for doc in docs:
                            filename, extensao = os.path.splitext(doc.arquivo.path)
                            with open(filename+'.txt','r') as f:
                                extra_file.write(f.read())
                                extra_file.write('\n')
                        extra_file.close()
                        extra_filename = os.path.join('output', extra_filename)
                        doc_extra = Documento.objects.create(nome=post.nome, email=post.email, arquivo=extra_filename,
                                                             tipo=post.tipo, chave=key)
                        return custom_redirect('nuvem', doc_extra.pk, chave=key)
                    else:
                        return custom_redirect('nuvem', docs[0].pk, chave=key)
            else:
                messages.error(request, 'Nenhum arquivo enviado')

        else:
            messages.error(request, 'ReCAPTCHA inválido. Por favor tente novamente!')

    return render(request, 'person_form.html', {'form': form, 'recaptcha': recaptcha})
