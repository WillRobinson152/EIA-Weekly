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
        """Fetches data from EIA API and returns Pandas DataFrame.

        Creates url based on sub1, sub2, frequency, facets and start and end 
        date parameters. Sends get request to url with class's API key. Returns
        response data as Pandas DataFrame.

        Args:
            sub1: String of first element in url after API key.
            sub2: String of second element in url after API key. For some requests,
            this element will have mutliple words separated by '/'.
            freq: String allowed by EIA (example: 'Weekly').
            facets: Dictionary with facet categories allowed by EIA ('Product' or 
            'Series', for example) as keys and lists of EIA codes for each category
            as values.

        Returns:
            A Pandas DataFrame with date values set to datetime.date.
        """
        url = f'https://api.eia.gov/v2/{sub1}/{sub2}/data/?api_key={self.key}&'
        url += self._addParameters(freq, facets, start, end)
        r = requests.get(url)
        df = pd.DataFrame(data=r.json()['response']['data'])
        df['period'] = pd.to_datetime(df.period).dt.date
        return df