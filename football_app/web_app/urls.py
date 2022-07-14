from django.urls import path
from . import views
from .views import line_chart, line_chart_json


#URL Conf
urlpatterns = [
    path('data/', views.table, name='data'),
    path('original', views.home_page_original, name='original'),
    path('', views.home_page, name='home'),
    path('analytics', views.fantasy_qb, name='analytics'),
    path('about', views.about, name='about'),
    path('chart', views.line_chart, name='line_chart'),
    path('chartJSON', views.line_chart_json, name='line_chart_json')
]