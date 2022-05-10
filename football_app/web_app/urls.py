from django.urls import path

from . import views

#URL Conf
urlpatterns = [
    path('data/', views.table, name='data'),
    path('', views.say_hello, name='home')
]