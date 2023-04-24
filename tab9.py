"""
A module to retrieve propane data from EIA's Table 9 csv file.

The module is used to retrieve the latest availabel data for the Weekly
Petroleum Status Report. Data include exports, imports, days of supply, 
production, product supplied, and national and regional inventory levels. 

Typical usage example:

  propane = Propane('your_api_key')
  df = propane.finalDf()
"""

import pandas as pd
from datetime import date

class Table9():
    """"
    Retrieves data from the EIA Table 9 csv from the weekly petroleum report. Report posted at:
    https://www.eia.gov/petroleum/supply/weekly/

    Retrieves latest data for propane inventories, exports, import, production 
    and product supplied.

    Attributes:
        url: String of url targeted in query for DataFrame.
    """
    def __init__(self):
        self.url = 'https://ir.eia.gov/wpsr/table9.csv'

    def getData(self):
        df = pd.read_csv(
            self.url,
            encoding='cp1252',
            na_values='– –',
            usecols=[0, 1, 2, 3, 4, 5]
        )
        m, d, y = df.columns[2].split('/')
        self.date = date(year=int(f'20{y}'), month=int(m), day=int(d))
        return df.rename(columns=dict(zip(df.columns, 
            ['commodity', 'category', 'current', 'week_ago', 'year_ago', 'two_years_ago'])))
    
    def filterData(self):
        df = self.getData()
        ### filter for these values
        commodities = [
            "Exports ", 
            "Imports ",
            "Product Supplied ",
            "Refiner and Blender Net Production ",
            "Stocks (Million Barrels) "
        ]
        categories = [
            "East Coast (PADD 1)",
            "Midwest (PADD 2)",
            "Gulf Coast (PADD 3)",
            "PADD's 4 & 5 ",
            "Propane/Propylene"
        ]
        df = df.loc[(df.commodity.isin(commodities))&(df.category.isin(categories)), 
                      :].reset_index(drop=True)
        # make all value columns floats
        for col in df.columns[2:]:
            df[col] = df[col].str.replace(',','').astype('float')
        ### split to separate DataFrames
        stocks = self.cleanData(df.loc[df.commodity=='Stocks (Million Barrels) '].loc[121:], 1000000)
        production = self.cleanData(df.loc[df.commodity=='Refiner and Blender Net Production '].loc[51:51], 1000)
        imports = self.cleanData(df.loc[df.commodity=='Imports '].loc[198:198], 1000)
        exports = self.cleanData(df.loc[df.commodity=='Exports '], 1000)
        supplied = self.cleanData(df.loc[df.commodity=='Product Supplied '], 1000)
        return stocks, production, imports, exports, supplied
    
    def cleanData(self, df, multiplier=1):
        df2 = df.copy()
        df2['category'] = \
        df2.category.replace(dict(zip(
            ['Propane/Propylene', "PADD's 4 & 5 "],
            ['U.S.', 'PADDs 4 and 5'])))
        for col in df2.columns[2:]:
            df2[col] = df2[col].mul(multiplier)
        df2['commodity'] = self.date
        df2.rename(columns={'commodity':'date', 'category':'region'}, inplace=True)
        return df2.reset_index(drop=True)
        
    def finalDf(self):
        stocks, production, imports, exports, supplied = self.filterData()
        stocks['process'] = 'Stocks'
        stocks['units'] = 'bbl'
        production['process'] = 'Production'
        production['units'] = 'b/d'
        exports['process'] = 'Exports'
        exports['units'] = 'b/d'
        imports['process'] = 'Imports'
        imports['units'] = 'b/d'
        supplied['process'] = 'Product Supplied'
        supplied['units'] = 'b/d'
        return pd.concat([stocks, production, exports, imports, supplied])\
            [['date', 'region', 'process', 'current', 'week_ago', 'year_ago', 'two_years_ago', 'units']].reset_index(drop=True)