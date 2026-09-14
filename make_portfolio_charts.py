import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dashboard' / 'artifacts'
OUT.mkdir(exist_ok=True)
df = pd.read_csv(ROOT / 'data' / 'manufacturing.csv')
plt.style.use('seaborn-v0_8-whitegrid')
BLUE, ORANGE, RED = '#2563eb', '#f59e0b', '#dc2626'

# 1 machine variation
fig, ax = plt.subplots(figsize=(9, 5.2))
order = sorted(df.Machine.unique())
ax.boxplot([df.loc[df.Machine == m, 'Diameter_mm'] for m in order], tick_labels=order,
           patch_artist=True, boxprops=dict(facecolor='#dbeafe', color=BLUE),
           medianprops=dict(color=RED, linewidth=2), whiskerprops=dict(color=BLUE), capprops=dict(color=BLUE))
ax.axhspan(19.7, 20.3, color='#dcfce7', alpha=.55, label='Diameter specification (19.7–20.3 mm)')
ax.axhline(20, color='#111827', linestyle='--', linewidth=1, label='Nominal 20.0 mm')
ax.set_title('Machine-to-machine diameter variation', loc='left', weight='bold', fontsize=15)
ax.set_xlabel('Machine'); ax.set_ylabel('Measured diameter (mm)'); ax.legend(frameon=False, loc='upper left')
fig.tight_layout(); fig.savefig(OUT / 'machine_variation.png', dpi=180); plt.close(fig)

# 2 Pareto
counts = df.loc[df.Defect_Type.notna(), 'Defect_Type'].value_counts().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(9, 5.2)); bars = ax.barh(counts.index, counts.values, color=BLUE)
for b, v in zip(bars, counts.values): ax.text(v + max(counts.values)*.015, b.get_y()+b.get_height()/2, f'{v:,}', va='center', fontsize=10)
ax.set_title('Primary inspection failure modes', loc='left', weight='bold', fontsize=15)
ax.set_xlabel('Parts assigned to primary failure mode'); ax.set_ylabel('')
ax.text(.99, .03, 'Simulation labels; surface finish is not measured Ra', transform=ax.transAxes, ha='right', fontsize=9, color='#4b5563')
fig.tight_layout(); fig.savefig(OUT / 'defect_pareto.png', dpi=180); plt.close(fig)

# 3 sensitivity
s = pd.read_csv(ROOT / 'results' / 'sensitivity.csv')
fig, ax = plt.subplots(figsize=(9, 5.2))
g = s.groupby('residual_offset_mm')['avoided_failures'].agg(['mean','min','max']).reset_index()
ax.fill_between(g.residual_offset_mm, g['min'], g['max'], color='#bfdbfe', alpha=.8, label='Observed range across 30 seeds')
ax.plot(g.residual_offset_mm, g['mean'], marker='o', color=ORANGE, linewidth=2.5, label='Mean avoided failures')
ax.set_title('How sensitive is the benefit to residual offset?', loc='left', weight='bold', fontsize=15)
ax.set_xlabel('Residual M3 offset after centering (mm)'); ax.set_ylabel('Avoided failures per 20,000 parts')
ax.legend(frameon=False); fig.tight_layout(); fig.savefig(OUT / 'centering_sensitivity.png', dpi=180); plt.close(fig)
