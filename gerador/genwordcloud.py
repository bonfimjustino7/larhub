import sys,os,re, glob
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from django.conf import settings

def generate(filename):
    excecoes = []
    for palavra in open('gerador/excecoes.txt').read().lower().split(','):
        excecoes.append(palavra.strip())
    for palavra in open('gerador/contexto.txt').read().lower().split(','):
        excecoes.append(palavra.strip())

    palavras = re.findall(r'\w+', filename)
    #palavras = open(filename)
    # Monta o texto final remove as palavras da lista de exceções e que sejam menores que 4 caracteres
    texto = ''
    frequencia = Counter()
    for palavra in list(palavras):
        if len(palavra) > 4 and palavra not in excecoes:
            texto += ' ' + palavra
            frequencia[palavra] += 1

    # Gera o arquivo CSV com as frequências
    """csv_filename = os.path.splitext(filename)[0] + '.csv'
    import csv
    with open(csv_filename, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for item in frequencia.most_common(60):
            writer.writerow(item)"""

    cloud = WordCloud(width=1200, height=800, max_words=60, scale=2).generate_from_frequencies(frequencia)

    # plt.figure(num=None, figsize=(12, 10), dpi=160, facecolor='w', edgecolor='k')
    # plt.imshow(cloud, interpolation="bilinear")
    # plt.axis("off")
    # plt.show()

    #image_filename = os.path.join(settings.MEDIA_URL, os.path.splitext(filename)[0] + '.jpg')
    cloud.to_file("media/usuario_pdf/nuvem_gerada.png")
    print('Imagem Gerada')

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