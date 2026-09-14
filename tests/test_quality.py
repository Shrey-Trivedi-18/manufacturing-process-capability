import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from generate_data import generate_production_data,generate_gage_rr_data
from analysis import inspect_dimensions,summary,validate,gage_analysis,sensitivity
class QualityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d=generate_production_data();cls.c=generate_production_data(process_centered=True)
 def test_boundaries(self):
  a,b=inspect_dimensions([19.7,20.3],[49.5,50.5]);self.assertFalse(a.any() or b.any())
 def test_outside_boundaries(self):
  a,b=inspect_dimensions([19.699,20.301],[49.499,50.501]);self.assertTrue(a.all() and b.all())
 def test_missing_rejected(self):
  with self.assertRaises(ValueError):inspect_dimensions([np.nan],[50])
 def test_nonfinite_rejected(self):
  with self.assertRaises(ValueError):inspect_dimensions([20],[np.inf])
 def test_known_baseline(self):
  s=summary(self.d);self.assertEqual((s['failures'],s['diameter_failures'],s['length_failures']),(1067,80,2))
 def test_known_centered(self):
  s=summary(self.c);self.assertEqual((s['failures'],s['diameter_failures'],s['length_failures']),(992,0,2))
 def test_no_length_failure_passes(self):self.assertTrue(self.d.loc[self.d.Length_Fail,'Inspection_Result'].eq('Fail').all())
 def test_primary_categories_reconcile(self):self.assertEqual(self.d.Defect_Type.ne('None').sum(),1067)
 def test_generator_reproducible(self):pd.testing.assert_frame_equal(self.d,generate_production_data())
 def test_only_m3_changes(self):
  pd.testing.assert_frame_equal(self.d.loc[self.d.Machine.ne('M3')],self.c.loc[self.c.Machine.ne('M3')]);np.testing.assert_allclose(self.d.loc[self.d.Machine.eq('M3'),'Diameter_mm']-self.c.loc[self.c.Machine.eq('M3'),'Diameter_mm'],.22)
 def test_length_unchanged(self):np.testing.assert_array_equal(self.d.Length_mm,self.c.Length_mm)
 def test_residual_offset(self):pd.testing.assert_frame_equal(self.d,generate_production_data(m3_offset_mm=.22))
 def test_duplicate_identifier_rejected(self):
  with self.assertRaises(ValueError):validate(pd.concat([self.d,self.d.iloc[:1]]))
 def test_misclassified_failure_rejected(self):
  x=self.d.copy();x.loc[x.Length_Fail,'Inspection_Result']='Pass'
  with self.assertRaises(AssertionError):validate(x)
 def test_grr(self):
  g=generate_gage_rr_data(self.d);r=gage_analysis(g);self.assertEqual(len(g),90);self.assertAlmostEqual(r['percent_study_variation'],9.133712278,7);self.assertEqual(r['ndc'],15)
 def test_incomplete_grr_rejected(self):
  with self.assertRaises(ValueError):gage_analysis(generate_gage_rr_data(self.d).iloc[:-1])
 def test_sensitivity_pairing(self):
  s=sensitivity(range(2));self.assertTrue(s.loc[s.residual_offset_mm.eq(.22),'avoided_failures'].eq(0).all())
 def test_committed_data(self):
  d=pd.read_csv(Path(__file__).resolve().parents[1]/'data/manufacturing.csv',keep_default_na=False);validate(d);self.assertEqual(summary(d),summary(self.d))
if __name__=='__main__':unittest.main()
