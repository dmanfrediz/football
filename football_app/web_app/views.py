from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import numpy as np
import json
import datetime as dt
import getpass as gt
from .models import Post

# Create your views here.

def say_hello(request):
    user = gt.getuser()
    return render(request, 'hello_football.html', context={'name': '{}'.format(user), 'title': 'Football App',
                                                           'posts': Post.objects.all()})


def table(request):
    df = pd.DataFrame(np.random.randint(0, 100, size=(15, 4)), columns=list('ABCD'))
    json_records = df.reset_index().to_json(orient='records')
    data = json.loads(json_records)
    context = {'d': data}
    return render(request, 'table_format.html', context)


# def home_page(request):
#     return render(request, 'hello_football.html',
#                   context={'date': str(dt.date.today()), 'title': 'Football App',
#                            'posts': Post.objects.all()})
