from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import numpy as np
import json
import datetime as dt
import os
import getpass as gt

# Create your views here.

# def say_hello(request):
#     user = gt.getuser()
#     return render(request, 'hello_football.html', context={'name': '{}'.format(user), 'title': 'Football App',
#                                                            'posts': Post.objects.all()})

config = open(os.path.dirname(os.path.realpath(__file__)) + '/test.config', "r")

with config as f:
    lines = f.readlines()
    columns = lines[0].strip()
    print(f"Columns={columns}")

#
# with open("secrets.txt") as f:
#     lines = f.readlines()
#     username = lines[0].strip()
#     password = lines[1].strip()
#     print(f"USERNAME={username}, PASSWORD={password}")

def table(request):
    df = pd.DataFrame(np.random.randint(0, 100, size=(15, 4)), columns=list(f'{columns}'))
    json_records = df.reset_index().to_json(orient='records')
    data = json.loads(json_records)
    context = {'d': data}
    return render(request, 'table_format.html', context)


def home_page_original(request):
    return render(request, 'hello_football.html',
                  context={'date': str(dt.date.today()), 'title': 'Football App'})


def home_page(request):
    return render(request, 'home_augur.html')
