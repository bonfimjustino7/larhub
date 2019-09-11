from django.urls import path
from .views import persons_list
from .views import persons_new
#from .views import home


urlpatterns = [
    path('', persons_new, name="person_new"),
    path('list/', persons_list, name="person_list"),
    #path('new/', persons_new, name="person_new"),

]
