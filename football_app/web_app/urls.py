from django.urls import path
from . import views

#URL Conf
urlpatterns = [
    path('data/', views.table, name='data'),
    path('original', views.home_page_original, name='original'),
    path('', views.home_page, name='home'),
]