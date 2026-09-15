import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'phase2_spc_capability'))
from study import generate,rules,limits,capability

class SPCChecks(unittest.TestCase):
    def test_subgroups_and_order(self):
        d=generate();self.assertEqual(len(d),700)
        self.assertTrue(d.groupby('Subgroup').size().eq(5).all())
        self.assertTrue(d.Run_Order.is_monotonic_increasing)
        self.assertEqual(d.Part_ID.nunique(),700)
        self.assertTrue(d.groupby('Subgroup').Phase.nunique().eq(1).all())
    def test_repeatability(self):
        self.assertTrue(generate().equals(generate()))
    def test_rule_boundaries(self):
        self.assertEqual(rules([3,3.01],0,1),['','T1'])
        self.assertIn('T2',rules([.1]*9,0,1)[8])
        self.assertNotIn('T2',rules([.1]*8,0,1)[7])
        self.assertIn('T3',rules(np.arange(6)/10,0,1)[5])
        self.assertNotIn('T3',rules([0,1,1,2,3,4],0,10)[5])
    def test_known_limits_and_indices(self):
        import pandas as pd
        g=pd.DataFrame({'Mean':[20.,20.], 'Range':[.2326,.2326]})
        l=limits(g); self.assertAlmostEqual(l['sigma_within'],.1)
        self.assertAlmostEqual(l['x_ucl'],20+3*.1/np.sqrt(5))
        d=pd.DataFrame({'Diameter_mm':[19.9,20.,20.1], 'Diameter_Fail':[False]*3})
        c=capability(d,g);self.assertAlmostEqual(c['Cp'],1.)
        self.assertAlmostEqual(c['Cpk'],1.)
    def test_conformance_inclusive(self):
        d=generate(); expected=(d.Diameter_mm<19.7)|(d.Diameter_mm>20.3)
        self.assertTrue(d.Diameter_Fail.equals(expected))

if __name__=='__main__':unittest.main()
