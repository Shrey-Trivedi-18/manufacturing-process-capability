"""Build the static presentation companion from corrected analysis outputs."""
from pathlib import Path
import sys,json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from analysis import validate
d=pd.read_csv(ROOT/'data/manufacturing.csv',keep_default_na=False);validate(d)
m=json.loads((ROOT/'dashboard/metrics.json').read_text());sens=pd.read_csv(ROOT/'results/sensitivity.csv')
INK='#203343';BLUE='#28647A';RED='#B24C36';GRAY='#63737D';LIGHT='#E0E6E9'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':INK,'text.color':INK,'axes.titleweight':'bold','axes.edgecolor':LIGHT,'xtick.color':GRAY,'ytick.color':GRAY})
fig=plt.figure(figsize=(15,10),facecolor='#FAFBFC')
fig.text(.055,.95,'What does machine centering actually change?',fontsize=24,weight='bold')
fig.text(.055,.915,'Simulated machining study | 20,000 parts | Paired baseline and ideal-centering scenarios',fontsize=11,color=GRAY)
b=m['baseline'];c=m['centered']
for x,label,value,note in [(.055,'BASELINE FAILURES',f'{b["failures"]:,}','Diameter, length and assigned defects'),(.36,'INSPECTION PASS RATE',f'{b["pass_rate"]:.3%}','Inclusive dimensional specification limits'),(.68,'NET FAILURES AVOIDED',str(b['failures']-c['failures']),f'Ideal centering; {c["failures"]:,} failures remain')]:
 fig.text(x,.862,label,fontsize=10,color=GRAY,weight='bold');fig.text(x,.817,value,fontsize=28,weight='bold');fig.text(x,.782,note,fontsize=10,color=GRAY)
ax=fig.add_axes([.085,.435,.39,.25],facecolor='white')
groups=[d.loc[d.Machine.eq(k),'Diameter_mm'] for k in ['M1','M2','M3','M4']]
bp=ax.boxplot(groups,vert=False,tick_labels=['M1','M2','M3','M4'],patch_artist=True,showfliers=False,widths=.5)
for patch,col in zip(bp['boxes'],[BLUE,BLUE,RED,BLUE]):patch.set_facecolor(col);patch.set_alpha(.65)
ax.axvline(19.7,color=GRAY,ls='--');ax.axvline(20.3,color=RED,ls='--');ax.axvline(20,color=GRAY,lw=.7)
ax.set_xlim(19.66,20.36);ax.set_xlabel('Measured diameter (mm)');ax.set_title('M3 is shifted toward the upper limit',loc='left',pad=15)
ax.text(0,-.28,'Boxes: median and quartiles; whiskers: 1.5 x IQR. Outliers omitted here.',transform=ax.transAxes,fontsize=8.5,color=GRAY)
ax2=fig.add_axes([.615,.435,.33,.25],facecolor='white');counts=pd.Series(m['primary_defects']).iloc[::-1]
bars=ax2.barh(counts.index,counts.values,color=[BLUE]*(len(counts)-1)+[RED],height=.65)
ax2.bar_label(bars,padding=5,fontsize=10);ax2.set_xlim(0,470);ax2.set_xlabel('Parts in each primary failure category')
ax2.set_title('Surface finish is the largest category',loc='left',pad=15);ax2.grid(axis='x',color=LIGHT,lw=.6);ax2.set_axisbelow(True)
ax3=fig.add_axes([.085,.105,.39,.22],facecolor='white');ax3.bar([0,1],[b['failures'],c['failures']],width=.48,color=[RED,BLUE])
for i,v in enumerate([b['failures'],c['failures']]):ax3.text(i,v+25,f'{v:,}',ha='center',weight='bold')
ax3.set_xticks([0,1],['Baseline','Ideal centering']);ax3.set_ylim(0,1250);ax3.set_ylabel('Failed parts');ax3.set_title('Total-yield benefit is limited',loc='left',pad=15)
ax4=fig.add_axes([.615,.105,.33,.22],facecolor='white');stats=sens.groupby('residual_offset_mm').avoided_failures.agg(['mean','min','max'])
ax4.fill_between(stats.index,stats['min'],stats['max'],color=BLUE,alpha=.15,label='Range across 30 seeds');ax4.plot(stats.index,stats['mean'],color=BLUE,marker='o',label='Mean')
ax4.set_ylim(bottom=0);ax4.set_xlabel('Residual M3 center offset (mm)');ax4.set_ylabel('Net failures avoided');ax4.set_title('Benefit depends on the remaining offset',loc='left',pad=15);ax4.legend(frameon=False,fontsize=8,loc='lower left')
fig.text(.055,.025,'Synthetic results, not realized savings. Sensitivity bands describe simulation seeds, not confidence in a factory intervention.',fontsize=9,color=GRAY)
fig.savefig(ROOT/'dashboard/quality_dashboard_preview.png',dpi=160,facecolor=fig.get_facecolor());plt.close(fig)
