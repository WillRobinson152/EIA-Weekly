"""
A module to retrieve propane data from the Energy Information Administration API v2.

The module is used to retrieve historical propane data relevant to the Weekly
Petroleum Status Report. Data include exports, imports, days of supply, 
production, product supplied, and national and regional inventory levels. 

Typical usage example:

  propane = Propane('your_api_key')
  df = propane.finalDf()
"""

from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd

from eq import EiaQuery

class Propane(EiaQuery):
    """
    Retrieves propane data from the EIA API v2. 
    
    API documentation available at: https://www.eia.gov/opendata/index.php.
    User must have an API key.

    Attributes:
        key: API key provided at initialization of class.
        sub1: String of first element in url after API key ('petroleum').
        sub2: String of second element in url after API key ('sum/sndw').
        freq: String of data frequency ('weekly').
        facets: Dictionary of facet categories and codes relevant to propane.
    """
    def __init__(self, apiKey):
        super().__init__(apiKey)
        self.sub1 = 'petroleum'
        self.sub2 = 'sum/sndw'
        self.freq = 'weekly'
        """
        *** Stock data for 2020 and on; historical data have other series codes
        and include propylene.
        """
        self.facets = {"series": [
            # US imports
            "WPRIM_NUS-Z00_2",
            # US production
            "WPRTP_NUS_2",
            # US product supplied
            "WPRUP_NUS_2",
            # US exports
            "W_EPLLPZ_EEX_NUS-Z00_MBBLD",
            # US days of supply
            "W_EPLLPZ_VSD_NUS_DAYS",
            # US stocks
            "WPRSTUS1",
            # East Coast stocks (PADD 1)
            "WPRSTP11",
            # Midwest stocks (PADD 2)
            "WPRSTP21",
            # Gulf Coast stocks (PADD 3)
            "WPRSTP31",
            # PADD 4 & 5 stocks
            "WPRST_R4N5_1"
        ]
    }

    def getDf(self, 
              start=str(date.today() - relativedelta(years=3)), end=None):
        return super().getDf(self.sub1, 
                             self.sub2, 
                             self.freq, 
                             self.facets, 
                             start, 
                             end)
    
    def cleanDf(self):
        df = self.getDf()
        # remove unneeded columns
        df = df.copy()[['period', 'area-name', 'process-name', 'value', 'units']]
        # rename regions in area-name
        regions = {'NA':'PADDs 4 and 5', 'PADD 3':'Gulf Coast (PADD 3)', 'PADD 2':'Midwest (PADD 2)', 'PADD 1':'East Coast (PADD 1)'}
        df['area-name'] = [regions[region] if region in regions.keys() else region for region in df['area-name']]
        # rename Stocks and Production in process-name
        df['process-name'] = df['process-name'].replace('Ending Stocks Excluding Propylene at Terminal','Stocks').replace('All Plants','Production')
        # convert thousands of barrels to barrels
        df.loc[df.units.isin(['MBBL', 'MBBL/D']), 'value'] = df.loc[df.units.isin(['MBBL', 'MBBL/D']), 'value'].mul(1000)
        # rename units
        df['units'] = df.units.replace('MBBL', 'bbl').replace('MBBL/D', 'b/d').replace('DAYS', 'days')
        # rename columns
        df.rename(columns={'period':'date',
                           'area-name':'region',
                           'process-name':'process',
                           'value':'current',
                           },
                  inplace=True)
        return df
    
    def shiftedDf(self, df):
        """
        Creates 52-row DataFrame with week_ago, year_ago, and two_years_ago columns.

        Sorts df by date, creates columns of value shifted 1 week, 52 weeks and 
        104 weeks with column names 'week_ago', 'year_ago', and 'two_years_ago'. 
        Drops nulls. Resets index. Converts floats to ints. Reorders columns.

        Args:
            df: A subset of cleanedDf as a Pandas DataFrame.

        Returns:
            A Pandas DataFrame.
        """
        shifted = df.copy()
        # sort by date
        shifted.sort_values('date', inplace=True)
        # create columns with data shifted by 1, 52 and 104 weeks
        shifted['week_ago'] = shifted.current.shift(1)
        shifted['year_ago'] = shifted.current.shift(52)
        shifted['two_years_ago'] = shifted.current.shift(104)
        # drop nulls
        shifted.dropna(inplace=True)
        shifted.reset_index(drop=True, inplace=True)
        return shifted[['date', 'region', 'process', 'current', 'week_ago',
                        'year_ago', 'two_years_ago', 'units']]
    
    def finalDf(self):
        """
        Generates DataFrame of all EIA weekly propane data with current, week_ago,
        year_ago, and two_years_ago values.

        Creates instance of EiaQuery with query parameters for propane to retrieve
        data from EIA API. Cleans data. Shifts data to create columns of historical
        values. Returns Pandas DataFrame.

        Returns:
            A Pandas DataFrame.
        """
        df = self.cleanDf()
        dfs = [
            self.shiftedDf(df.copy().loc[df.process=='Exports']),
            self.shiftedDf(df.copy().loc[df.process=='Imports']),
            self.shiftedDf(df.copy().loc[df.process=='Product Supplied']),
            self.shiftedDf(df.copy().loc[df.process=='Days of Supply']),
            self.shiftedDf(df.copy().loc[df.process=='Production']),
            self.shiftedDf(df.copy().loc[(df.process=='Stocks')&(df.region=='U.S.')]),
            self.shiftedDf(df.copy().loc[(df.process=='Stocks')&(df.region=='East Coast (PADD 1)')]),
            self.shiftedDf(df.copy().loc[(df.process=='Stocks')&(df.region=='Midwest (PADD 2)')]),
            self.shiftedDf(df.copy().loc[(df.process=='Stocks')&(df.region=='Gulf Coast (PADD 3)')]),
            self.shiftedDf(df.copy().loc[(df.process=='Stocks')&(df.region=='PADDs 4 and 5')]),
        ]
        return pd.concat(dfs).reset_index(drop=True)

