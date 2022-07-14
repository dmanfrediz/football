from abc import ABC

from django.shortcuts import render
from django.http import HttpResponse
from .models import FantasyQb
import pandas as pd
import numpy as np
import json
import datetime as dt
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView, BaseLineOptionsChartView
from chartjs.colors import next_color


# Create your views here.

# def say_hello(request):
#     user = gt.getuser()
#     return render(request, 'hello_football.html', context={'name': '{}'.format(user), 'title': 'Football App',
#                                                            'posts': Post.objects.all()})


def table(request):
    df = pd.DataFrame(np.random.randint(0, 100, size=(15, 4)), columns=list('ABCD'))
    json_records = df.reset_index().to_json(orient='records')
    data = json.loads(json_records)
    context = {'d': data}
    return render(request, 'table_format.html', context)


def home_page_original(request):
    return render(request, 'hello_football.html',
                  context={'date': str(dt.date.today()), 'title': 'Football App'})


def home_page(request):
    return render(request, 'home_augur.html')


def about(request):
    return render(request, 'about.html')


def fantasy_qb(request):
    fantasy = FantasyQb()
    df = fantasy.data
    json_records = df.reset_index().to_json(orient='records')
    data = json.loads(json_records)
    context = {'d': data}
    return render(request, 'fantasy_qb.html', context)


class LineChartJSONView(BaseLineOptionsChartView, ABC):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self._colors = {
        #     'gray': (202, 201, 197),  # Light gray
        #     'red': (171, 9, 0),  # Red
        #     'orange': (166, 78, 46),  # Light orange
        #     'yellow': (255, 190, 67),  # Yellow
        #     'green': (163, 191, 63),  # Light green
        #     'blue': (95, 158, 160),  # Steel blue
        #     'pink': (140, 5, 84),  # Pink
        #     'brown': (166, 133, 93),  # Light brown
        #     'blue': (75, 64, 191) # Red blue
        #     }
        # self.color = self._colors[color]

        self._colors = [
            (122, 159, 191),  # Light blue
            (163, 191, 63),  # Light green
            (171, 9, 0),  # Red
            (202, 201, 197),  # Light gray
            (166, 78, 46),  # Light orange
            (255, 190, 67),  # Yellow
            (140, 5, 84),  # Pink
            (166, 133, 93),  # Light brown
            (75, 64, 191),  # Red blue
            (237, 124, 60),  # orange
            (95, 158, 160)  # Cadet blue
        ]

    def get_context_data(self, **kwargs):
        context = super(BaseLineChartView, self).get_context_data(**kwargs)
        context.update({"labels": self.get_labels(), "datasets": self.get_datasets(), "options": {"yAxes": [{
            "gridLines": {"zeroLineColor": '#ffcc33'}}]
            }})
        return context

    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return ["January", "February", "March", "April", "May", "June", "July"]

    def get_providers(self):
        """Return names of datasets."""
        return ["Central", "Eastside", "Westside"]

    def get_dataset_options(self, index, color):
        default_opt = {
            "backgroundColor": "rgba(%d, %d, %d, 0.3)" % color,
            "borderColor": "rgba(%d, %d, %d, 0.5)" % color,
            "pointBackgroundColor": "rgba(%d, %d, %d, 1)" % color,
            "pointBorderColor": "rgb(0,0,0)",
        }
        return default_opt

    def get_data(self):
        """Return 3 datasets to plot."""

        return [[75, 44, 92, 11, 44, 95, 35],
                [41, 92, 18, 3, 73, 87, 92],
                [87, 21, 94, 3, 90, 13, 65]]

    def get_colors(self, colors):
        return next_color(colors)

    def get_datasets(self):
        datasets = []
        color_generator = self.get_colors(self._colors)
        data = self.get_data()
        providers = self.get_providers()
        num = len(providers)
        for i, entry in enumerate(data):
            color = tuple(next(color_generator))
            dataset = {"data": entry}
            dataset.update(self.get_dataset_options(i, color))
            if i < num:
                dataset["label"] = providers[i]  # series labels for Chart.js
                dataset["name"] = providers[i]  # HighCharts may need this
            datasets.append(dataset)
        return datasets


line_chart = TemplateView.as_view(template_name='chart_js_test.html')
line_chart_json = LineChartJSONView.as_view()
