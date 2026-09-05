"""Rebuild the README presentation preview from the committed production CSV.

This is a static companion to the editable Excel dashboard, not an Excel screenshot.
Run from the repository root: python scripts/build_dashboard_preview.py
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, MultipleLocator
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch
import matplotlib.dates as mdates

ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'data/manufacturing.csv',keep_default_na=False)
df['Date']=pd.to_datetime(df['Date'])
failed=df.Inspection_Result.eq('Fail')
def ppk(s):
    return min(20.30-s.mean(),s.mean()-19.70)/(3*s.std(ddof=1))
machine=df.groupby('Machine').Diameter_mm.agg(ppk)
daily=df.assign(Failed=failed).groupby('Date').Failed.mean()
counts=df.loc[failed,'Defect_Type'].value_counts()
heat=df.assign(Failed=failed).pivot_table(index='Machine',columns='Shift',values='Failed',aggfunc='mean')
summary={'parts':len(df),'failed':int(failed.sum()),'fpy':float(1-failed.mean()),'ppm':int(failed.mean()*1e6),'overall_ppk':ppk(df.Diameter_mm),'machine_ppk':machine.to_dict(),'defect_counts':counts.to_dict(),'date_start':str(df.Date.min().date()),'date_end':str(df.Date.max().date())}
(ROOT/'dashboard/metrics.json').write_text(json.dumps(summary,indent=2)+'\n')

INK='#172B3A'; MUTED='#596B78'; BLUE='#276587'; RED='#B74732'; BG='#F3F5F6'; GRID='#DEE5E8'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,'axes.labelcolor':MUTED,'xtick.color':MUTED,'ytick.color':MUTED,'axes.edgecolor':GRID,'axes.titleweight':'bold','axes.titlesize':13,'figure.facecolor':BG})
fig=plt.figure(figsize=(16,11),dpi=180)
def txt(x,y,s,size=11,color=INK,weight='normal',**kwargs):
    return fig.text(x,y,s,fontsize=size,color=color,weight=weight,**kwargs)
txt(.045,.947,'Manufacturing process performance',25,weight='bold')
txt(.045,.914,'Simulated precision-machining line   /   20,000 parts   /   Jan 5–Mar 5, 2026',11,MUTED)
txt(.955,.949,'BASELINE',10,MUTED,weight='bold',ha='right')
fig.add_artist(plt.Line2D([.045,.955],[.893,.893],transform=fig.transFigure,color=GRID,lw=1))
metrics=[('FIRST-PASS YIELD',f'{summary["fpy"]:.1%}',f'{len(df)-int(failed.sum()):,} passed inspection',INK),('DEFECTIVE PARTS',f'{summary["failed"]:,}',f'{summary["ppm"]:,} per million parts',INK),('OVERALL DIAMETER Ppk',f'{summary["overall_ppk"]:.2f}','Mixed-machine baseline',INK),('M3 DIAMETER Ppk',f'{machine["M3"]:.2f}','Below the 1.33 study reference',RED)]
for i,(label,val,note,color) in enumerate(metrics):
    x=.045+i*.235
    txt(x,.862,label,10,MUTED,weight='bold');txt(x,.818,val,27,color,weight='bold');txt(x,.788,note,10,MUTED)

def panel(rect,title,subtitle):
    x,y,w,h=rect
    fig.add_artist(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.007,rounding_size=0.008',facecolor='white',edgecolor=GRID,lw=.7,transform=fig.transFigure,zorder=-1))
    txt(x+.016,y+h-.029,title,13,weight='bold');txt(x+.016,y+h-.052,subtitle,9.5,MUTED)

panel((.045,.421,.437,.327),'Diameter performance by machine','Ppk uses overall sample SD within each machine.')
ax=fig.add_axes([.095,.466,.35,.202]);bars=ax.bar(machine.index,machine.values,color=[BLUE,BLUE,RED,BLUE],width=.52,zorder=3)
ax.set_ylim(0,3.45);ax.set_yticks([0,1,2,3]);ax.axhline(1.33,color=MUTED,lw=1,ls=(0,(4,3)));ax.text(3.5,1.40,'1.33',fontsize=9,ha='right',color=MUTED)
ax.bar_label(bars,fmt='%.2f',padding=6,fontsize=11,weight='bold');ax.grid(axis='y',color=GRID,lw=.7,zorder=0)

panel((.511,.421,.437,.327),'Daily defective-part rate','All recorded inspection failures; daily production volumes vary.')
ax2=fig.add_axes([.562,.466,.36,.202]);ax2.plot(daily.index,daily.values,color=BLUE,lw=1.7);ax2.axhline(failed.mean(),color=MUTED,lw=1,ls=(0,(4,3)))
ax2.set_ylim(0,.105);ax2.yaxis.set_major_formatter(PercentFormatter(1,decimals=0));ax2.yaxis.set_major_locator(MultipleLocator(.02));ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2));ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'));ax2.grid(axis='y',color=GRID,lw=.7)
ax2.text(.02,.95,f'Volume-weighted baseline: {failed.mean():.2%}',transform=ax2.transAxes,fontsize=9,color=MUTED,va='top')

panel((.045,.095,.437,.293),'Defect Pareto','One assigned defect per failed part; categories are mutually exclusive.')
ax3=fig.add_axes([.155,.142,.29,.174]);ordered=counts.iloc[::-1];bar3=ax3.barh(ordered.index,ordered.values,color=[BLUE]*(len(ordered)-1)+[RED],height=.60);ax3.set_xlim(0,480);ax3.set_xticks([0,200,400]);ax3.grid(axis='x',color=GRID,lw=.7);ax3.set_axisbelow(True);ax3.bar_label(bar3,padding=5,fontsize=10)
txt(.062,.114,f'Surface finish: {counts.iloc[0]/counts.sum():.1%} of failures. Top three categories: {counts.iloc[:3].sum()/counts.sum():.1%}.',9.5,MUTED)

panel((.511,.095,.437,.293),'Defective-part rate by machine and shift','Darker cells indicate higher failure rates. Percent of inspected parts.')
ax4=fig.add_axes([.576,.153,.318,.145]);cmap=LinearSegmentedColormap.from_list('rates',['#F6EDE5','#DFB59E','#B74732']);ax4.imshow(heat.values,vmin=0,vmax=.08,cmap=cmap,aspect='auto')
ax4.set_xticks(range(3),['Shift A','Shift B','Shift C']);ax4.xaxis.tick_top();ax4.set_yticks(range(4),heat.index);ax4.tick_params(length=0,pad=9)
for r in range(4):
    for c in range(3):
        v=heat.iloc[r,c];ax4.text(c,r,f'{v:.1%}',ha='center',va='center',fontsize=12,color='white' if v>.07 else INK,weight='bold')
txt(.53,.114,'Shift C has the highest observed failure rate on each machine.',9.5,MUTED)
for axis in [ax,ax2,ax3,ax4]:
    for spine in axis.spines.values():spine.set_visible(False)
    axis.tick_params(length=0)
txt(.045,.057,'INTERPRETATION',9,MUTED,weight='bold')
txt(.145,.057,'M3 centering is the dimensional issue. Surface finish remains the largest overall defect category.',10)
txt(.045,.028,'Source: data/manufacturing.csv. Static companion to quality_dashboard.xlsx. Synthetic results; stable process capability is not established.',9,MUTED)
fig.savefig(ROOT/'dashboard/quality_dashboard_preview.png',dpi=180,facecolor=BG)
plt.close(fig)
print(json.dumps(summary,indent=2))
