from datetime import date
from dateutil.relativedelta import relativedelta

from eq import EiaQuery

class Propane(EiaQuery):
    def __init__(self, apiKey):
        super().__init__(apiKey)
        self.sub1 = 'petroleum'
        self.sub2 = 'sum/sndw'
        self.freq = 'weekly'
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