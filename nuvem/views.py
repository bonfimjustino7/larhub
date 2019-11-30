import os
import uuid
import json
import urllib
import detectlanguage

from django.shortcuts import render, redirect, get_object_or_404

from .models import Documento
from .forms import DocumentoForm
from django.conf import settings
from gerador.genwordcloud import generate
from django.contrib import messages
from gerador.pdf2txt import pdf2txt

''' Configuration API LANGUAGE DETECT'''
detectlanguage.configuration.api_key = settings.API_KEY_LANGUAGE


def home(request):
    return render(request, 'home.html')


def nuvem(request, id):
    documento = Documento.objects.get(pk=id)

    nome_arquivo = documento.arquivo.path
    prefix, file_extension = os.path.splitext(nome_arquivo)
    if not os.path.exists(prefix+'.txt'):
        pdf2txt(documento.arquivo.path)

    nome_arquivo = prefix+'.txt'

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
            if request.FILES:
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
                    doc = Documento.objects.create(nome=post.nome, email=post.email, arquivo=f)
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
                    doc_extra = Documento.objects.create(nome=post.nome, email=post.email, arquivo=extra_filename)
                    return redirect('nuvem', doc_extra.pk)
                else:
                    return redirect('nuvem', docs[0].pk)
            else:
                messages.error(request, 'Nenhum arquivo enviado')

        else:
            messages.error(request, 'ReCAPTCHA inválido. Por favor tente novamente!')

    return render(request, 'person_form.html', {'form': form, 'recaptcha': recaptcha})
