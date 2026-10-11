import unittest
from datetime import date
import pandas as pd
from market_data import fetch_prices, normalize_ticker

class MarketDataTests(unittest.TestCase):
    def test_symbol(self):
        self.assertEqual(normalize_ticker(' spy '),'SPY')
        with self.assertRaises(ValueError): normalize_ticker('SPY QQQ')
    def test_adjustment_and_inclusive_end(self):
        captured={}
        class Fake:
            def history(self,**kwargs):
                captured.update(kwargs)
                return pd.DataFrame({'Close':[100.,101.]},index=pd.date_range('2020-01-01',periods=2,tz='America/New_York'))
        prices,meta=fetch_prices('SPY',date(2020,1,1),date(2020,1,2),lambda _:Fake())
        self.assertEqual(captured['end'],'2020-01-03')
        self.assertTrue(captured['auto_adjust'])
        self.assertEqual(len(prices),2)
        self.assertEqual(prices.index[0],pd.Timestamp('2020-01-01'))
        self.assertEqual(meta['ticker'],'SPY')
    def test_empty(self):
        class Fake:
            def history(self,**kwargs): return pd.DataFrame()
        with self.assertRaises(ValueError):fetch_prices('SPY',date(2020,1,1),date(2020,2,1),lambda _:Fake())
    def test_provider_error(self):
        class Fake:
            def history(self,**kwargs): raise RuntimeError('unavailable')
        with self.assertRaisesRegex(ValueError,'Could not load'):
            fetch_prices('SPY',date(2020,1,1),date(2020,2,1),lambda _:Fake())
    def test_date_order(self):
        with self.assertRaises(ValueError):fetch_prices('SPY',date(2020,2,1),date(2020,1,1))
