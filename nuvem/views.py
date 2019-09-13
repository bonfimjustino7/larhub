import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from wordcloud import WordCloud, STOPWORDS

from .models import Person
from .forms import PersonForm
from PIL import Image
import os
from django.conf import settings
from gerador.genwordcloud import generate


def gerarNuvem(request):
    return 2


def home(request):
    return render(request, 'home.html')


def persons_list(request):
    person = Person.objects.last()
    generate(person.pdf.path)

    contexto = {
        'person': person
    }
    return render(request, 'person.html', contexto)


def persons_new(request):
    form = PersonForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        texto2 = form.cleaned_data['pdf']
        #print(dir(texto2))
        #print(str(texto2.read()))

        """alice_mask = np.array(Image.open("media/usuario_pdf/cloud.png"))
        stopwords = set(STOPWORDS)

        # Adicionando a lista stopwords em português
        new_words = []
        with open("media/usuario_pdf/palavras.txt", 'r') as f:
            [new_words.append(word) for line in f for word in line.split()]

        new_stopwords = stopwords.union(new_words)
        wc = WordCloud(background_color="white", max_words=200, mask=alice_mask,
                       stopwords=new_stopwords, contour_width=3, contour_color='steelblue')
        # generate word cloud
        wc.generate(str(texto2.read()))

        # store to file
        wc.to_file("media/usuario_pdf/alice.png")
        print("Imagem criada com sucesso")"""
        form.save()
        return redirect('person_list')
    return render(request, 'person_form.html', {'form': form})