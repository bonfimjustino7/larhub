from django.urls import path
from .views import persons_new
from .views import persons_list


urlpatterns = [
    path('', persons_new, name="person_new"),
    path('list/', persons_list, name="person_list"),

]
