
from django.db import models
from gerador.genwordcloud import generate

class Documento(models.Model):
    num_doc = models.CharField(max_length=50)

    def __str__(self):
        return self.num_doc


class Person(models.Model):
    nome = models.CharField(max_length=30)
    idade = models.IntegerField()
    pdf = models.FileField(upload_to='usuario_pdf', null=True, blank=True)

    def gerar(self):
        for t in Person.objects.all():
            generate(t.pdf)

    #doc = models.OneToOneField(Documento, null=True, blank=True, on_delete=models.CASCADE)

   # def __str__(self):
   #     return self.first_name + ' ' + self.last_name
