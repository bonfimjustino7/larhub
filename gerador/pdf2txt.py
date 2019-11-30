import sys
import os
from io import StringIO
from pdfminer3.converter import PDFConverter
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import PDFPageAggregator
from pdfminer3.pdfpage import PDFPage
from pdfminer3.layout import LTContainer, LTChar, LTText, LTTextBox, LTFigure, LTTextContainer
from pdfminer3.layout import LAParams


class SimpleTextConverter(PDFConverter):

    def __init__(self, rsrcmgr, outfp, codec='utf-8', pageno=1, laparams=None):
        PDFConverter.__init__(self, rsrcmgr, outfp, codec=codec, pageno=pageno, laparams=laparams)
        return

    def write_text(self, text):
        self.outfp.write(text)
        return

    def receive_layout(self, ltpage):
        def render(item):
            if isinstance(item, LTTextContainer):
                texto = item.get_text()
                self.write_text(texto)
                self.write_text('\n')
            elif isinstance(item, LTContainer):
                for child in item:
                    render(child)
            elif isinstance(item, LTText):
                self.write_text(item.get_text())

        render(ltpage)
        return


def pdf2txt(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    text_filename = os.path.splitext(fname)[0] + '.txt'
    textfile = open(text_filename, 'w')
    manager = PDFResourceManager()
    converter = SimpleTextConverter(manager, textfile, laparams=LAParams(all_texts=True))
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    textfile.close()
    return


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
    for page in PDFPage.get_pages(fp, check_extractable=False):
        interpreter.process_page(page)
        layout = device.get_result()
        pagina = []
        for element in layout:
            if isinstance(element, LTTextBox) or isinstance(element, LTText):
                texto = element.get_text()
                if texto:
                    if len(texto) < 2:
                        pagina[-1] += texto
                    else:
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
        else:
            pagina.pop(0)

        for linha in pagina:
            textfile.write("%s\n" % linha)
    textfile.close()


if __name__ == '__main__':
    pdf2txt(sys.argv[1])
    # pdfparser(sys.argv[1])
