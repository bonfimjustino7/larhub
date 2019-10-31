from django.urls import path
from .views import new_doc
from .views import nuvem


urlpatterns = [
    path('', new_doc, name="new_doc"),
    path('nuvem/<int:id>', nuvem, name="nuvem"),

]
