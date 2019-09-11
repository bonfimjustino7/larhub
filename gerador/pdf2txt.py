import sys
import os
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBoxHorizontal
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams

def pdfparser(filename):

    fp = open(filename, 'rb')
    rsrcmgr = PDFResourceManager()
    codec = 'utf-8'
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Process each page contained in the document.
    paginas = []
    for page in PDFPage.get_pages(fp,check_extractable=False):
        interpreter.process_page(page)
        layout = device.get_result()
        pagina = []
        for element in layout:
            if isinstance(element, LTTextBoxHorizontal):
                texto = element.get_text()
                if texto:
                    pagina += texto.split("\n")

        # limpa linhas vazias
        pagina_limpa = []
        for linha in pagina:
            if linha.strip():
                pagina_limpa.append(linha.strip())

        if len(pagina_limpa) > 0:
            paginas.append(pagina_limpa)

    text_filename = os.path.splitext(filename)[0]+'.txt'
    textfile = open(text_filename, 'w')

    # remove header
    header_candidato = ''
    for pagina in paginas:
        if pagina[0].strip() != header_candidato:
            header_candidato = pagina[0].strip()
            print('***:%s' % header_candidato)
        else:
            pagina.pop(0)

        for linha in pagina:
            textfile.write("%s\n" % linha)
    textfile.close()

if __name__ == '__main__':
    pdfparser(sys.argv[1])
