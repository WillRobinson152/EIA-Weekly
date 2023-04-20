"""A module to query the Energy Information Administration API v2.

The module is used to retrieve historical data relevant to the Weekly
Petroleum Status Report.

Typical usage example:

  query = EiaQuery('your_api_key')
  df = query.getDf('petroleum',
                  'move/wkly',
                  'weekly',
                  {'series': ['W_EPLLPZ_EEX_NUS-Z00_MBBLD', 
                              'WPRIM_NUS-Z00_2']
                  },
                  '2023-04-12',
                  '2023-04-19',
                 )
"""

import requests
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

class EiaQuery:
    """"
    Retrieves data from the EIA API v2. 
    
    API documentation available at: https://www.eia.gov/opendata/index.php.
    User must have an API key.

    Attributes:
        key: API key provided at initialization of class.
    """
    def __init__(self, apiKey):
        self.key = apiKey

    def _addParameters(self, freq, facets, start=None, end=None):
        s = f'frequency={freq}&data[0]=value'
        for k, v in facets.items():
            for item in v:
                s += f'&facets[{k}][]={item}'
        if start:
            s += f'&start={start}'
        if end:
            s += f'&end={end}'
        return s
    
    def getDf(self, 
              sub1, 
              sub2, 
              freq, 
              facets,
              start=str(date.today() - relativedelta(years=3)),
              end=None
              ):
        url = f'https://api.eia.gov/v2/{sub1}/{sub2}/data/?api_key={self.key}&'
        url += self._addParameters(freq, facets, start, end)
        r = requests.get(url)
        df = pd.DataFrame(data=r.json()['response']['data'])
        df['period'] = pd.to_datetime(df.period).dt.date
        return df