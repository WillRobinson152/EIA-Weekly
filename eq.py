import requests
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

class eiaQuery:
    """"
    Retrieves data from the EIA API v2. API documentation at:
    https://www.eia.gov/opendata/index.php
    """
    def __init__(self, apiKey):
        self.urlStart = 'https://api.eia.gov/v2/'
        self.key = f'?api_key={apiKey}&'

    def addParameters(self, freq, facets, start=None, end=None):
        s = f'frequency={freq}&data[0]=value'
        for k, v in facets.items():
            for item in v:
                s += f'&facets[{k}][]={item}'
        if start:
            s += f'&start={start}'
        if end:
            s += f'&end={end}'
        return s
    
    def query(self,
              sub1,
              sub2,
              freq,
              facets,
              start=str(date.today() - relativedelta(years=3)),
              end=None):
        params = self.addParameters(
            freq=freq,
            facets=facets,
            start=start,
            end=end
        )
        url = f'{self.urlStart}{sub1}{sub2}data/{self.key}{params}'
        return url
    
    def getDf(self, url):
        r = requests.get(url)
        df = pd.DataFrame(data=r.json()['response']['data'])
        df['period'] = pd.to_datetime(df.period).dt.date
        return df