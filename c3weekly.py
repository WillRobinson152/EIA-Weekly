import pandas as pd

from eqC3 import Propane
from tab9 import Table9

class PropaneWeekly:
    def __init__(self, apiKey):
        self.apiKey = apiKey 
        self.c3 = Propane(self.apiKey)
        self.t9 = Table9()

    def joinDfs(self):
        return pd.concat([self.c3.finalDf(), self.t9.finalDf()]).reset_index(drop=True)

    def handleCurrentWeek(self):
        df = self.joinDfs()
        df.drop_duplicates(inplace=True)
        if len(df.loc[(df.date==df.date.max())&(df.process=='Days of Supply')]) == 0:
            us_stocks = df.loc[(df.process=='Stocks')&(df.region=='U.S.'), 'current'].tail(1).sum()
            supplied_4wk_avg = df.loc[df.process=='Product Supplied', 'current'].tail(4).mean()
            old_stocks = df.loc[(df.process=='Stocks')&(df.region=='U.S.')&(df.date==df.date.max()), ['year_ago', 'two_years_ago']]
            old_supplied = df.loc[df.process=='Product Supplied', ['year_ago', 'two_years_ago']].tail(4)
            days_supply = pd.DataFrame(data={
                'date':[df.date.max()],
                'region': ['U.S.'],
                'process': ['Days of Supply'],
                'current': [round(us_stocks / supplied_4wk_avg, 1)],
                'week_ago': [df.loc[df.process == 'Days of Supply', 'current'].iloc[-1]],
                'year_ago': [round(old_stocks.year_ago.sum() / old_supplied.year_ago.mean(), 1)],
                'two_years_ago': [round(old_stocks.two_years_ago.sum() / old_supplied.two_years_ago.mean(), 1)],
                'units': ['days']
            })
            df = pd.concat([df, days_supply]).reset_index(drop=True)
        return df