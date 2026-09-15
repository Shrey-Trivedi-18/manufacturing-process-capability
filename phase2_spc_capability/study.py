"""Separate, time-ordered teaching simulation. No Phase 1 records are relabeled."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
SEED=20260914
N=5
D2=2.326
A2=3/(D2*np.sqrt(N))
D3=0.0
D4=2.114
LSL,USL=19.7,20.3

def generate():
    rng=np.random.default_rng(SEED)
    rows=[]
    # Windows fixed before any outcomes; no seed searching or deletion of alarms.
    windows=[('reference',1,40,20.00),('setup_shift',41,60,20.27),
             ('rebaseline',61,100,20.00),('verification',101,140,20.00)]
    for phase,lo,hi,mean in windows:
        for group in range(lo,hi+1):
            for part in range(1,N+1):
                true=mean+rng.normal(0,.045)
                measured=true+rng.normal(0,.006)
                rows.append(dict(Part_ID=f'SPC-{group:03}-{part}',Subgroup=group,
                    Within_Subgroup_Order=part,Run_Order=(group-1)*N+part,
                    Timestamp=(pd.Timestamp('2026-09-07 08:00')+pd.Timedelta(minutes=(group-1)*15+part-1)).isoformat(),
                    Phase=phase,True_Diameter_mm=true,Diameter_mm=measured,
                    Setup_Code='OFFSET_027' if phase=='setup_shift' else 'VERIFIED_ZERO',
                    Diameter_Fail=not LSL<=measured<=USL))
    return pd.DataFrame(rows)

def limits(g):
    return dict(center=float(g.Mean.mean()),rbar=float(g.Range.mean()),
        x_lcl=float(g.Mean.mean()-A2*g.Range.mean()),x_ucl=float(g.Mean.mean()+A2*g.Range.mean()),
        r_lcl=0.,r_ucl=float(D4*g.Range.mean()),sigma_within=float(g.Range.mean()/D2))

def rules(values,center,sigma):
    """Nelson-style tests 1,2,3 only. Flag final point of each qualifying window."""
    v=np.asarray(values); out=[]
    for i,x in enumerate(v):
        hits=[]
        if abs(x-center)>3*sigma: hits.append('T1')
        if i>=8:
            w=v[i-8:i+1]-center
            if np.all(w>0) or np.all(w<0): hits.append('T2')
        if i>=5:
            dv=np.diff(v[i-5:i+1])
            if np.all(dv>0) or np.all(dv<0): hits.append('T3')
        out.append(','.join(hits))
    return out

def capability(d,g):
    mean=float(d.Diameter_mm.mean()); sw=float(g.Range.mean()/D2); so=float(d.Diameter_mm.std(ddof=1))
    return dict(n=len(d),mean=mean,within_sd=sw,overall_sd=so,
        Cp=(USL-LSL)/(6*sw),Cpk=min(USL-mean,mean-LSL)/(3*sw),
        Pp=(USL-LSL)/(6*so),Ppk=min(USL-mean,mean-LSL)/(3*so),
        failures=int(d.Diameter_Fail.sum()),failure_rate=float(d.Diameter_Fail.mean()),
        shapiro_p=float(stats.shapiro(d.Diameter_mm).pvalue),
        lag1=float(d.Diameter_mm.autocorr()),
        zero_failure_upper95=float(1-.05**(1/len(d))) if not d.Diameter_Fail.any() else None)

def plot_style():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,
        'axes.spines.right':False,'axes.titleweight':'bold','savefig.facecolor':'#f8fafc','figure.facecolor':'#f8fafc'})

def export_plot(fig,name):
    fig.text(.06,.025,'SIMULATED PRODUCTION  |  Seed 20260914  |  Shrey Trivedi',fontsize=9,color='#475569')
    fig.savefig(ROOT/'charts'/name,dpi=180); plt.close(fig)

def run():
    ROOT.mkdir(exist_ok=True); (ROOT/'charts').mkdir(exist_ok=True)
    d=generate(); d.to_csv(ROOT/'spc_data.csv',index=False)
    g=d.groupby(['Subgroup','Phase'],sort=False).Diameter_mm.agg(Mean='mean',Range=lambda x:x.max()-x.min()).reset_index()
    ref=limits(g[g.Phase=='reference']); new=limits(g[g.Phase=='rebaseline'])
    g['X_LCL']=np.where(g.Subgroup<=100,ref['x_lcl'],new['x_lcl'])
    # Explicit comparison streams: 1-60 uses reference; 61-100 estimates new limits; 101-140 holds them fixed.
    chunks=[]
    for phases,lim,label in [(['reference','setup_shift'],ref,'reference limits'),(['rebaseline'],new,'new baseline estimates'),(['verification'],new,'frozen new limits')]:
        z=g[g.Phase.isin(phases)].copy()
        z['Center']=lim['center']; z['X_LCL']=lim['x_lcl']; z['X_UCL']=lim['x_ucl']
        z['R_Center']=lim['rbar']; z['R_LCL']=0.; z['R_UCL']=lim['r_ucl']; z['Limits_Source']=label
        z['X_Rules']=rules(z.Mean,lim['center'],lim['sigma_within']/np.sqrt(N))
        z['R_Rules']=np.where(z.Range>lim['r_ucl'],'T1','')
        chunks.append(z)
    g=pd.concat(chunks,ignore_index=True); g.to_csv(ROOT/'subgroup_results.csv',index=False)
    alarms=g[(g.X_Rules!='')|(g.R_Rules!='')]; alarms.to_csv(ROOT/'alarm_log.csv',index=False)
    caps={}
    for phase in d.Phase.unique():
        cap=capability(d[d.Phase==phase],g[g.Phase==phase])
        cap['x_alarm_count']=int(((g.Phase==phase)&(g.X_Rules!='')).sum())
        cap['r_alarm_count']=int(((g.Phase==phase)&(g.R_Rules!='')).sum())
        cap['interpretation']=('unstable against reference; descriptive indices only' if phase=='setup_shift' else ('provisional: selected-rule signal requires review' if cap['x_alarm_count'] or cap['r_alarm_count'] else 'no selected-rule signals in finite window'))
        caps[phase]=cap
    caps['pooled_invalid']=capability(d,g)
    caps['pooled_invalid']['interpretation']='mixed regimes; not a capability claim'
    output=dict(seed=SEED,subgroup_size=N,constants=dict(d2=D2,A2=A2,D3=D3,D4=D4),
        reference_limits=ref,new_limits=new,capability=caps,
        first_shift_alarm=int(alarms[alarms.Phase=='setup_shift'].Subgroup.min()))
    (ROOT/'results.json').write_text(json.dumps(output,indent=2)+'\n')
    pd.DataFrame(caps).T.to_csv(ROOT/'capability_summary.csv',index_label='Phase')
    plot_style()
    fig,axs=plt.subplots(2,1,figsize=(12,7.6),sharex=True,gridspec_kw={'height_ratios':[2,1]})
    for ax,col,cl,ll,ul in [(axs[0],'Mean','Center','X_LCL','X_UCL'),(axs[1],'Range','R_Center','R_LCL','R_UCL')]:
        ax.plot(g.Subgroup,g[col],'-o',ms=3,color='#2563eb',lw=1)
        for key,style,color in [(cl,'-','#0f766e'),(ll,'--','#dc2626'),(ul,'--','#dc2626')]:
            ax.plot(g.Subgroup,g[key],style,color=color,lw=1)
        for low,high,c in [(40.5,60.5,'#fee2e2'),(60.5,100.5,'#e0f2fe')]:ax.axvspan(low,high,color=c,zorder=0)
        a=g[g.X_Rules!=''] if col=='Mean' else g[g.R_Rules!='']
        ax.scatter(a.Subgroup,a[col],color='#dc2626',s=28,zorder=3)
        ax.grid(axis='y',alpha=.15)
    axs[0].set_title('A setup shift is detected with frozen reference limits',loc='left',pad=32)
    for x,txt in [(20,'REFERENCE'),(50,'SHIFT'),(80,'REBASELINE'),(120,'VERIFICATION')]:axs[0].text(x,1.015,txt,transform=axs[0].get_xaxis_transform(),ha='center',fontsize=9)
    axs[0].set_ylabel('Subgroup mean (mm)'); axs[1].set_ylabel('Range (mm)'); axs[1].set_xlabel('Subgroup in production order (5 consecutive parts each)')
    fig.subplots_adjust(left=.09,right=.96,bottom=.12,top=.84,hspace=.18); export_plot(fig,'01_xbar_r.png')
    fig,ax=plt.subplots(figsize=(11,6.3))
    for phase,color,label in [('reference','#2563eb','Reference'),('setup_shift','#dc2626','Shift / quarantined'),('verification','#0f766e','Verification')]:
        ax.hist(d[d.Phase==phase].Diameter_mm,bins=np.linspace(19.65,20.5,43),density=True,histtype='step',lw=2,color=color,label=label)
    for v in [LSL,USL]:ax.axvline(v,color='#111827',ls='--')
    ax.set(xlabel='Measured shaft diameter (mm)',ylabel='Density',title='Conformance and statistical control answer different questions')
    ax.legend(frameon=False); fig.subplots_adjust(left=.10,right=.95,top=.88,bottom=.15); export_plot(fig,'02_diameter_distributions.png')
    fig,axs=plt.subplots(1,2,figsize=(11,5.8))
    for ax,phase in zip(axs,['reference','verification']):
        stats.probplot(d[d.Phase==phase].Diameter_mm,dist='norm',plot=ax)
        ax.set_title(phase.title()+f" | Shapiro p={caps[phase]['shapiro_p']:.3f}")
        ax.set_ylabel('Measured diameter (mm)')
    fig.suptitle('Normality diagnostics for the two comparison windows',fontsize=16,weight='bold'); fig.subplots_adjust(left=.09,right=.95,bottom=.17,top=.82,wspace=.3); export_plot(fig,'03_normality.png')
    fig,ax=plt.subplots(figsize=(11,6.3)); phases=['reference','setup_shift','verification']; x=np.arange(3)
    for i,(metric,color) in enumerate([('Cp','#94a3b8'),('Cpk','#2563eb'),('Pp','#cbd5e1'),('Ppk','#0f766e')]):
        bars=ax.bar(x+(i-1.5)*.19,[caps[p][metric] for p in phases],width=.18,label=metric,color=color)
        ax.bar_label(bars,fmt='%.2f',padding=3,fontsize=9)
    ax.set_xticks(x,['Reference\n200 parts','Shift: descriptive only\n100 parts','Verification: provisional\n200 parts / T3 alert'])
    ax.set_ylabel('Index (unitless)');ax.set_title('Capability is interpreted only after the stability review',loc='left')
    ax.legend(ncols=4,frameon=False);ax.set_ylim(0,3.5)
    fig.subplots_adjust(left=.09,right=.95,bottom=.19,top=.87);export_plot(fig,'04_capability.png')
    return d,g,output

if __name__=='__main__':
    _,_,m=run();print(json.dumps(m,indent=2))
