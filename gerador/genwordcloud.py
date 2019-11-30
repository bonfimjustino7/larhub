import sys
import os
import re
import glob
import csv

from collections import Counter
from wordcloud import WordCloud
from django.conf import settings
from difflib import SequenceMatcher


def generate(nome_arquivo, language='pt'):
    excecoes = []
    sw_filename = os.path.join(settings.BASE_DIR, 'gerador', 'stopwords-%s.txt' % language)
    print(sw_filename)
    if language and os.path.exists(sw_filename):
        for linha in open(sw_filename).read().lower().split('\n'):
            for palavra in linha.split(','):
                excecoes.append(palavra.strip())

    try:
        arquivo = open(nome_arquivo, 'r')
    except UnicodeDecodeError as erro:
        arquivo = open(nome_arquivo, 'r', encoding='ISO-8859-1')

    # Busca cabeçalhos e rodapés
    frequencia = Counter()
    for linha in arquivo.read().lower().split('\n'):
        if len(linha) > 3:
            frequencia[linha] += 1
    arquivo.close()

    duplicadas = {}
    for linha in frequencia.most_common():
        if linha[1] > 3:
            duplicadas[linha[0]] = 0
        else:
            break

    palavras = []
    prefix, file_extension = os.path.splitext(nome_arquivo)
    arq_limpo = open(prefix+'.dedup', 'w')
    for linha in open(nome_arquivo, 'r').read().lower().split('\n'):
        if linha not in duplicadas:
            arq_limpo.write(linha+'\n')
            palavras += re.findall(r'\w+', linha)
    arq_limpo.close()

    # Monta o texto final remove as palavras da lista de exceções e que sejam menores que 3 caracteres
    texto = ''
    frequencia = Counter()
    for palavra in palavras:
        if len(palavra) > 3 and palavra not in excecoes:
            texto += ' ' + palavra
            frequencia[palavra] += 1

    # Gera o arquivo CSV com as frequências
    csv_filename = prefix + '.csv'

    with open(csv_filename, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for item in frequencia.most_common(100):
            writer.writerow(item)

    cloud = WordCloud(width=1200, height=800, max_words=50, scale=2, background_color='white')
    cloud.generate_from_frequencies(frequencia)
    cloud.to_file(prefix+'.png')

    image_filename = os.path.basename(prefix)
    image_filename = os.path.join(settings.MEDIA_URL, 'usuario_pdf', image_filename+'.png')
    return image_filename


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = None
    if filename and os.path.isfile(filename):
        generate(filename)
    else:
        for filename in glob.glob("files/*.txt"):
            generate(filename)
