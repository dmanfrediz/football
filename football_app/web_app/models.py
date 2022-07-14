from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import os
import pymongo
import pandas as pd


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class FantasyQb(models.Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = ''
        self.password = ''
        self.get_mongo_credentials()
        self.data = self.get_data()

    def get_mongo_credentials(self):
        config = open(os.path.dirname(os.path.realpath(__file__)) + '/test.config', "r")

        with config as f:
            lines = f.readlines()
            self.username = lines[0].strip()
            self.password = lines[1].strip()
            # print(f"USERNAME={self.username}, PASSWORD={self.password}")

    @staticmethod
    def _net_value(performance, price):
        x = performance * 100
        return round(x - price, 2)

    def get_data(self, *args, **kwargs):
        conn_str = f"mongodb+srv://{self.username}:{self.password}@footballmongo.i1eva28.mongodb.net/?retryWrites=true&w=majority"

        client = pymongo.MongoClient(conn_str, tls=True)

        db = client.football_data
        coll = db.fantasy_2021
        df = pd.DataFrame(list(coll.find()))
        df = df.drop(columns=['FDP', 'Price_f', 'YHP', 'Price_y'])

        # Split homes and away games
        df['away'] = df['Oppt'].apply(lambda x: len(x.split('@')) - 1)
        df['DKP'] = df['DKP'].apply(lambda x: float(x))
        df['Price'] = df['Price'].apply(lambda x: float(x))
        df_hva = df[['DKP', 'Price', 'Name', 'Team', 'Pos', 'away']]
        df_hva_std = df[['DKP', 'Price', 'Name', 'Team', 'Pos', 'away']]

        # group by with mean and std agg functions
        df_hva_std = df_hva.groupby(by=['Pos', 'away', 'Team', 'Name']).std()
        df_hva = df_hva.groupby(by=['Pos', 'away', 'Team', 'Name']).mean()

        # isolate by QB position
        qb_h_m = df_hva.loc['QB', 0]
        # qb_h['DKP_stdev'] = np.std(qb_h['DKP'])
        qb_a_m = df_hva.loc['QB', 1]

        qb_h_std = df_hva_std.loc['QB', 0]
        qb_a_std = df_hva_std.loc['QB', 1]

        # Fix column names
        qb_h_m = qb_h_m.rename(columns={'DKP': 'DKP_home_mean', 'Price': 'Price_home_mean'})
        qb_a_m = qb_a_m.rename(columns={'DKP': 'DKP_away_mean', 'Price': 'Price_away_mean'})
        qb_a_std = qb_a_std.rename(columns={'DKP': 'DKP_away_std', 'Price': 'Price_away_std'})
        qb_h_std = qb_h_std.rename(columns={'DKP': 'DKP_home_std', 'Price': 'Price_home_std'})

        # merge data
        qb = qb_h_m.merge(qb_a_m, how='left', on=['Team', 'Name'])
        qb = qb.merge(qb_h_std, how='left', on=['Team', 'Name'])
        qb = qb.merge(qb_a_std, how='left', on=['Team', 'Name'])

        qb['road_consistency'] = qb['DKP_home_std'] - qb['DKP_away_std']
        qb['road_performance_avg'] = qb['DKP_away_mean'] - qb['DKP_home_mean']
        qb['road_price_avg'] = qb['Price_away_mean'] - qb['Price_home_mean']
        qb_2 = qb.reset_index()
        # qb.head()
        qb_res = qb_2[['Team', 'Name', 'road_consistency', 'road_performance_avg', 'road_price_avg', 'DKP_home_mean']]

        # Drop NaNs and sort
        qb_res = qb_res.dropna()
        qb_res = qb_res[qb_res['DKP_home_mean'] >= 15]
        qb_res['net_value'] = self._net_value(performance=qb_res['road_performance_avg'],
                                              price=qb_res['road_price_avg'])
        qb_res = qb_res[['Team', 'Name', 'net_value', 'road_performance_avg', 'road_price_avg', 'road_consistency',
                         'DKP_home_mean']]
        qb_res = qb_res.sort_values('net_value', ascending=False)
        qb_res['road_consistency'] = qb_res['road_consistency'].apply(lambda x: round(x, 2))
        qb_res['road_performance_avg'] = qb_res['road_performance_avg'].apply(lambda x: round(x, 2))
        qb_res['DKP_home_mean'] = qb_res['DKP_home_mean'].apply(lambda x: round(x, 2))
        qb_res['road_price_avg'] = qb_res['road_price_avg'].apply(lambda x: round(x, 2))
        qb_res = qb_res.reset_index(drop=True)
        return qb_res
