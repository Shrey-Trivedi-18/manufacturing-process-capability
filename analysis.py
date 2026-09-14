"""Shared, reproducible calculations for the simulated machining case study."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from generate_data import generate_production_data

ROOT = Path(__file__).resolve().parent


def inspect_dimensions(diameter, length):
    """Inclusive specification boundaries; missing values must not pass."""
    diameter = np.asarray(diameter, dtype=float)
    length = np.asarray(length, dtype=float)
    if not np.isfinite(diameter).all() or not np.isfinite(length).all():
        raise ValueError('Missing or nonfinite measurements cannot be classified as passes')
    return ((diameter < 19.7) | (diameter > 20.3),
            (length < 49.5) | (length > 50.5))


def validate(data):
    if data.empty or data.Part_ID.duplicated().any():
        raise ValueError('Data must have unique part identifiers and at least one row')
    df, lf = inspect_dimensions(data.Diameter_mm, data.Length_mm)
    np.testing.assert_array_equal(df, data.Diameter_Fail)
    np.testing.assert_array_equal(lf, data.Length_Fail)
    failed = data.Inspection_Result.eq('Fail')
    if not data.Inspection_Result.isin(['Pass', 'Fail']).all():
        raise ValueError('Unknown inspection result')
    np.testing.assert_array_equal(failed, df | lf | data.Defect_Type.ne('None'))
    np.testing.assert_array_equal(failed, data.Defect_Type.ne('None'))


def summary(data):
    validate(data)
    n = len(data)
    failed = int(data.Inspection_Result.eq('Fail').sum())
    return dict(parts=n, failures=failed, passes=n-failed, pass_rate=(n-failed)/n,
                ppm=failed/n*1e6, diameter_failures=int(data.Diameter_Fail.sum()),
                length_failures=int(data.Length_Fail.sum()))


def gage_analysis(g):
    if g.groupby(['Part_ID', 'Operator']).size().nunique() != 1 or g.duplicated(['Part_ID','Operator','Trial']).any():
        raise ValueError('Balanced crossed measurements with unique trials required')
    p, o, t = g.Part_ID.nunique(), g.Operator.nunique(), g.Trial.nunique()
    if min(p,o,t) < 2 or len(g) != p*o*t:
        raise ValueError('Incomplete crossed design')
    grand = g.Diameter_mm.mean()
    pm = g.groupby('Part_ID').Diameter_mm.mean()
    om = g.groupby('Operator').Diameter_mm.mean()
    cm = g.groupby(['Part_ID','Operator']).Diameter_mm.mean()
    ms_p = o*t*((pm-grand)**2).sum()/(p-1)
    ms_o = p*t*((om-grand)**2).sum()/(o-1)
    ms_i = t*sum((v-pm.loc[a]-om.loc[b]+grand)**2 for (a,b),v in cm.items())/((p-1)*(o-1))
    residual = g.Diameter_mm - g.set_index(['Part_ID','Operator']).index.map(cm)
    ms_e = (residual**2).sum()/(p*o*(t-1))
    parts=max((ms_p-ms_i)/(o*t),0)
    operator=max((ms_o-ms_i)/(p*t),0)
    interaction=max((ms_i-ms_e)/t,0)
    grr=ms_e+operator+interaction
    return dict(repeatability_var=float(ms_e), operator_var=float(operator), interaction_var=float(interaction),
                part_var=float(parts), grr_var=float(grr), grr_sd=float(np.sqrt(grr)),
                percent_study_variation=float(100*np.sqrt(grr/(grr+parts))),
                percent_tolerance=float(100*6*np.sqrt(grr)/.6),
                ndc=int(np.floor(1.41*np.sqrt(parts/grr))))


def machine_summary(d):
    return d.assign(Failed=d.Inspection_Result.eq('Fail')).groupby('Machine').agg(
        Parts=('Part_ID','size'), Failures=('Failed','sum'), Failure_Rate=('Failed','mean'),
        Diameter_Failures=('Diameter_Fail','sum'), Length_Failures=('Length_Fail','sum'),
        Mean_Diameter_mm=('Diameter_mm','mean'), SD_Diameter_mm=('Diameter_mm','std'))


def sensitivity(seeds=range(30)):
    """Paired common-random-number scenarios; no claim of factory uncertainty."""
    rows=[]
    for seed in seeds:
        base=summary(generate_production_data(seed=seed))
        for offset in [0.00,0.05,0.10,0.15,0.22]:
            s=summary(generate_production_data(seed=seed,m3_offset_mm=offset))
            rows.append(dict(seed=seed, residual_offset_mm=offset,
                             failures=s['failures'], diameter_failures=s['diameter_failures'],
                             pass_rate=s['pass_rate'], avoided_failures=base['failures']-s['failures']))
    return pd.DataFrame(rows)


def run():
    d=pd.read_csv(ROOT/'data/manufacturing.csv',keep_default_na=False)
    g=pd.read_csv(ROOT/'data/gage_rr.csv')
    b=summary(d)
    centered=generate_production_data(process_centered=True)
    c=summary(centered)
    m=machine_summary(d)
    rr=gage_analysis(g)
    sens=sensitivity()
    out=ROOT/'results'; out.mkdir(exist_ok=True)
    sens.to_csv(out/'sensitivity.csv',index=False)
    m.to_csv(out/'machine_summary.csv')
    d.loc[d.Length_Fail,['Part_ID','Length_mm','Inspection_Result']].to_csv(out/'length_exceptions.csv',index=False)
    categories=d.loc[d.Inspection_Result.eq('Fail'),'Defect_Type'].value_counts()
    metrics=dict(baseline=b,centered=c,gage=rr,
                 primary_defects={k:int(v) for k,v in categories.items()},
                 source_sha256=hashlib.sha256((ROOT/'data/manufacturing.csv').read_bytes()).hexdigest(),
                 scenario='seed 42, paired ideal centering',sensitivity_seeds=30,
                 machines=json.loads(m.reset_index().to_json(orient='records')))
    (ROOT/'dashboard/metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    # Prepared row-level evidence for the workbook. All exported records are retained.
    cols=['Part_ID','Machine','Shift','Diameter_mm','Length_mm','Defect_Type']
    prepared=d[cols].copy()
    prepared['Failed']=d.Inspection_Result.eq('Fail').astype(int)
    prepared['Diameter_Fail']=d.Diameter_Fail.astype(int)
    prepared['Length_Fail']=d.Length_Fail.astype(int)
    prepared.to_json(out/'workbook_rows.json',orient='values')
    return d,g,metrics,sens


if __name__ == '__main__':
    _,_,metrics,_=run()
    print(json.dumps(metrics,indent=2))
