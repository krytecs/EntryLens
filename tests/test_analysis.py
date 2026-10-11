import unittest
import numpy as np
import pandas as pd
from analysis import validate, cagr, windows, path_metrics

class CalculationTests(unittest.TestCase):
    def series(self, values, dates=None):
        return pd.Series(values, index=pd.to_datetime(dates or pd.date_range('2020-01-01', periods=len(values)).tolist()))
    def test_flat(self):
        s=pd.Series(100.,index=pd.bdate_range('2020-01-01','2023-01-01'))
        self.assertEqual(cagr(s),0)
        self.assertTrue((windows(s,1).cagr==0).all())
    def test_calendar_growth(self):
        s=self.series([100,121],['2020-01-01','2022-01-01'])
        expected=1.21**(365.2425/731)-1
        self.assertAlmostEqual(cagr(s),expected)
    def test_recovered_drawdown(self):
        m=path_metrics(self.series([100,80,90,100]))
        self.assertAlmostEqual(m['max_drawdown'],-.2)
        self.assertEqual(m['recovery_days'],3)
    def test_unrecovered(self):
        m=path_metrics(self.series([100,80,90]))
        self.assertTrue(np.isnan(m['recovery_days']))
        self.assertIn('Unrecovered',m['recovery_status'])
    def test_invalid(self):
        for prices in [[100,0],[100,float('inf')],[100,float('nan')]]:
            with self.assertRaises(ValueError):
                validate(pd.DataFrame({'date':['2020-01-01','2020-01-02'],'adjusted_close':prices}))
        with self.assertRaises(ValueError):
            validate(pd.DataFrame({'date':['2020-01-01']*2,'adjusted_close':[1,2]}))
    def test_anniversary(self):
        s=self.series([100,110,120],['2020-01-01','2021-01-04','2022-01-04'])
        w=windows(s,1)
        self.assertEqual(w.iloc[0]['end'],pd.Timestamp('2021-01-04'))
    def test_no_incomplete_windows(self):
        s=self.series([100,110],['2020-01-01','2020-06-01'])
        self.assertTrue(windows(s,1).empty)
    def test_benchmark_matched(self):
        s=pd.Series(np.arange(100,900),index=pd.date_range('2020-01-01',periods=800))
        w=windows(s,1,s.copy())
        self.assertTrue((w.excess_cagr==0).all())
    def test_future_does_not_change_completed_windows(self):
        s=pd.Series(np.arange(100.,1300.),index=pd.date_range('2020-01-01',periods=1200))
        original=windows(s,1)
        changed=s.copy(); changed.iloc[900:]*=2
        revised=windows(changed,1)
        pd.testing.assert_frame_equal(original[original.end<s.index[900]],revised[revised.end<s.index[900]])

if __name__=='__main__': unittest.main()
