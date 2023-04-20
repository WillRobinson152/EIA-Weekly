import unittest
import sys
# adding eiaWeekly to the system path
sys.path.insert(0, '/Users/robinsonw/Documents/Python Scripts/')
from eiaWeekly import EiaQuery

import pandas as pd

class TestEiaQuery(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestEiaQuery, self).__init__(*args, **kwargs)
        with open('eiaWeekly/tests/key.txt') as file:
            self.key = file.read()

    def test_exim2weeks(self):
        query = EiaQuery(self.key)
        df = query.getDf('petroleum',
                        'move/wkly',
                        'weekly',
                        {'series': ['W_EPLLPZ_EEX_NUS-Z00_MBBLD', 
                                    'WPRIM_NUS-Z00_2']
                        },
                        '2023-04-12',
                        '2023-04-19',
                        )
        df2 = pd.read_csv('eiaWeekly/tests/eq_test.csv')
        df2.period = pd.to_datetime(df2.period).dt.date
        pd.testing.assert_frame_equal(df, df2)

if __name__ == '__main__':
    unittest.main()
