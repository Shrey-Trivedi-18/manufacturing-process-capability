"""Rebuild Phase 2, inspection examples, Minitab inputs and the PDF portfolio."""
from pathlib import Path
import sys,json,csv,shutil,html
import numpy as np
import pandas as pd
from scipy import stats
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak
from reportlab.lib.enums import TA_LEFT
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'phase2_spc_capability'))
from study import run
from analysis import gage_analysis

BLUE=colors.HexColor('#1d4ed8');INK=colors.HexColor('#14243b');MUTED=colors.HexColor('#536579');PALE=colors.HexColor('#eff6ff')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleQE',fontName='Helvetica-Bold',fontSize=27,leading=32,textColor=INK,spaceAfter=18))
styles.add(ParagraphStyle(name='SubQE',fontName='Helvetica-Bold',fontSize=17,leading=21,textColor=BLUE,spaceAfter=12))
styles.add(ParagraphStyle(name='BodyQE',fontSize=10.2,leading=15,textColor=INK,spaceAfter=9))
styles.add(ParagraphStyle(name='CellQE',fontSize=8.3,leading=11,textColor=INK))
def p(t,style='BodyQE'):return Paragraph(html.escape(t).replace('&lt;br/&gt;','<br/>'),styles[style])
def table(rows,widths):
    t=Table([[p(str(v),'CellQE') for v in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,0),(-1,0),1,BLUE),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#dce3eb'))]))
    return t
def footer(c,doc):
    c.setStrokeColor(BLUE);c.line(42,40,570,40);c.setFont('Helvetica',8);c.setFillColor(MUTED)
    c.drawString(42,27,'QE-001  |  SIMULATED CASE STUDY  |  Shrey Trivedi  |  14 Sep 2026')
    c.drawRightString(570,27,str(doc.page))
def page(title,subtitle):return [p(title,'TitleQE'),p(subtitle),Spacer(1,10)]
def chart(path,width=520):
    from PIL import Image as PILImage
    with PILImage.open(path) as im:w,h=im.size
    return Image(str(path),width=width,height=width*h/w)

def inspection():
    out=ROOT/'drawing_and_inspection';out.mkdir(exist_ok=True)
    rows=[]
    for id,spec,value,unit,passed in [('D01','19.70 to 20.30',20.014,'mm',True),('L01','49.50 to 50.50',50.06,'mm',True),('H01','4.95 to 5.05',5.02,'mm',True),('E01','<=0.05',.018,'mm',True),('F01','<=0.10',.041,'mm',True),('S01','<=3.2',2.4,'um',True)]:
        rows.append(dict(Record='FP-001',Characteristic=id,Specification=spec,Simulated_Value=value,Unit=unit,Result='Pass' if passed else 'Fail'))
    # Straight axis endpoint distances after datum/clocking alignment.
    h=[]
    for name,end1,end2 in [('FP-001',.035,.045),('BOUNDARY',.085,.085),('CHALLENGE',.090,.090)]:
        size=5.02;bonus=size-4.95;allowed=.10+bonus;actual=2*max(abs(end1),abs(end2))
        h.append(dict(Record=name,Hole_Size_mm=size,Endpoint1_Radial_mm=end1,Endpoint2_Radial_mm=end2,
                      Position_Diameter_mm=actual,Bonus_mm=bonus,Allowed_Diameter_mm=allowed,
                      Result='Pass' if 4.95<=size<=5.05 and actual<=allowed+1e-12 else 'Fail'))
    rows.append(dict(Record='FP-001',Characteristic='H02',Specification='position <=0.17 at size5.02',Simulated_Value=.09,Unit='mm',Result='Pass'))
    pd.DataFrame(rows).to_csv(out/'first_piece_records.csv',index=False)
    pd.DataFrame(h).to_csv(out/'hole_position_examples.csv',index=False)
    return rows,h

def minitab(d,m):
    dest=ROOT/'minitab'/'inputs';dest.mkdir(exist_ok=True,parents=True)
    shutil.copyfile(ROOT/'data/gage_rr.csv',dest/'gage_rr.csv')
    for phase in d.Phase.unique():d[d.Phase==phase][['Subgroup','Diameter_mm']].to_csv(dest/f'spc_{phase}.csv',index=False)
    d1=pd.read_csv(ROOT/'data/manufacturing.csv',keep_default_na=False)
    d1[['Machine','Diameter_mm']].to_csv(dest/'anova.csv',index=False)
    rr=gage_analysis(pd.read_csv(ROOT/'data/gage_rr.csv'))
    anova=stats.f_oneway(*[g.Diameter_mm for _,g in d1.groupby('Machine')])
    vals=[('GRR',k,v) for k,v in rr.items()]+[('ANOVA','F',float(anova.statistic)),('ANOVA','p',float(anova.pvalue)),('ANOVA','DF_between',3),('ANOVA','DF_within',19996)]
    for phase in ['reference','rebaseline','verification']:
        vals += [(phase,k,m['capability'][phase][k]) for k in ['mean','within_sd','overall_sd','Cp','Cpk','Pp','Ppk']]
    vals += [('reference_limits',k,v) for k,v in m['reference_limits'].items()]
    vals += [('new_limits',k,v) for k,v in m['new_limits'].items()]
    pd.DataFrame(vals,columns=['Analysis','Metric','Python']).to_csv(ROOT/'minitab/python_reference.csv',index=False)
    comparisons=pd.DataFrame(vals,columns=['Analysis','Metric','Python']);comparisons['Minitab']='';comparisons['Difference']='';comparisons['Status']='NOT RUN - SIGN IN REQUIRED'
    comparisons.to_csv(ROOT/'minitab/comparison.csv',index=False)

def drawing():
    path=ROOT/'drawing_and_inspection/gdandt_learning_drawing.pdf'
    c=canvas.Canvas(str(path),pagesize=(792,612));c.setTitle('QE-001 Rev B - GD&T inspection learning drawing')
    c.setStrokeColor(INK);c.setFillColor(INK);c.rect(24,24,744,564)
    c.setFont('Helvetica-Bold',20);c.drawString(44,552,'QE-001  |  SHAFT INSPECTION EXERCISE')
    c.setFont('Helvetica',10);c.drawString(44,532,'REV B LEARNING ADDENDUM  /  dimensions in mm  /  schematic, not to scale')
    # Principal view: OD silhouette, hole facing viewer, end B.
    x,y,w,h=105,300,330,132;c.rect(x,y,w,h);c.circle(x+w/2,y+h/2,16.5)
    c.setDash(8,3);c.line(80,y+h/2,460,y+h/2);c.line(x+w/2,y+h/2-28,x+w/2,y+h/2+28);c.setDash()
    def arrow(a,b,xx,yy):
        c.line(a,b,xx,yy);ang=np.arctan2(yy-b,xx-a)
        path=c.beginPath();path.moveTo(xx,yy);path.lineTo(xx-7*np.cos(ang-.4),yy-7*np.sin(ang-.4));path.lineTo(xx-7*np.cos(ang+.4),yy-7*np.sin(ang+.4));path.close();c.drawPath(path,fill=1)
    c.line(x,435,x,480);c.line(x+w,435,x+w,480);arrow(x+w/2-40,465,x,465);arrow(x+w/2+40,465,x+w,465)
    c.setFont('Helvetica',11);c.drawCentredString(x+w/2,462,'50 +/-0.50');c.drawString(449,464,'[L01]')
    # basic 25
    c.line(x,295,x,263);c.line(x+w/2,339,x+w/2,263);arrow(166,273,x,273);arrow(209,273,x+w/2,273)
    c.rect(172,265,30,18);c.drawCentredString(187,270,'25')
    arrow(58,366,105,366);c.rect(37,356,21,21);c.drawCentredString(47.5,362,'B')
    # FCF draw symbols rather than font-dependent glyphs
    def frame(xx,yy,kind,cells):
        widths=[28]+[max(27,7*len(t)+14) for t in cells]
        left=xx
        for wi,t in zip(widths,['']+cells):c.rect(left,yy,wi,22);c.drawCentredString(left+wi/2,yy+7,t);left+=wi
        cx,cy=xx+14,yy+11
        if kind=='position':c.circle(cx,cy,6);c.line(cx-9,cy,cx+9,cy);c.line(cx,cy-9,cx,cy+9)
        elif kind=='perp':c.line(cx-8,cy-6,cx+8,cy-6);c.line(cx,cy-6,cx,cy+8)
        else:c.circle(cx,cy,5);c.line(cx-8,cy-8,cx,cy+8);c.line(cx,cy-8,cx+8,cy+8)
    arrow(340,345,284,354);c.drawString(342,345,'DIA 5 +/-0.05 THRU [H01]')
    c.line(343,342,343,260)
    frame(343,238,'position',['DIA 0.10 (M)','A','B']);c.drawString(343,223,'[H02]')
    # end view OD with size datum A
    c.circle(604,383,66);c.setDash(8,3);c.line(525,383,683,383);c.line(604,304,604,462);c.setDash()
    arrow(655,290,649,335);c.drawString(565,274,'DIA 20 +/-0.30 [D01]');c.line(653,270,653,251);c.rect(642.5,230,21,21);c.drawCentredString(653,236,'A')
    frame(541,200,'cyl',['0.10']);c.drawString(641,207,'[F01]');arrow(568,224,556,338)
    frame(50,220,'perp',['0.05','A']);c.drawString(181,227,'B face [E01]');arrow(88,242,105,309)
    c.setFont('Helvetica',10)
    notes=['1. A = OD cylindrical datum feature; B = left end face. Datum A precedes B.',
           '2. Hole axis: basic 90 deg to A; basic 25 from B. Clocking about A is unrestricted.',
           '3. OD surface finish Ra <=3.2 micrometres [S01]; define profilometer procedure before use.',
           '4. Position example assumes straight ideal bore. Evaluate full axis and size; do not use center alone.',
           '5. Learning drawing only. Native Onshape Rev A retained separately; this is not its revised export.',
           '6. No manufacturing release, formal FAI approval or standards-conformance certification.']
    for i,note in enumerate(notes):c.drawString(44,169-i*19,note)
    c.setFont('Helvetica-Bold',9);c.drawString(44,38,'SHREY TRIVEDI  |  SIMULATED INSPECTION PLANNING  |  2026-09-14');c.drawRightString(749,38,'SHEET 1 / 1')
    c.save()

def diagrams():
    import matplotlib.pyplot as plt
    target=ROOT/'quality_documents'
    fig,ax=plt.subplots(figsize=(12,6));ax.set(xlim=(0,12),ylim=(0,6));ax.axis('off')
    ax.annotate('',xy=(10.6,3),xytext=(.4,3),arrowprops=dict(arrowstyle='->',lw=2,color='#1d4ed8'))
    ax.text(10.65,3,'D01\nHigh\ndiameter',va='center',fontsize=13,weight='bold')
    branches=[(1.5,5,'METHOD','Wrong compensation\nDemonstrated in model'),(4.5,5,'MACHINE','Tool / holder shift\nNot modeled'),(7.5,5,'MEASUREMENT','Zero bias\nPhysical check needed'),(1.5,1,'MATERIAL','Stock change\nNot modeled'),(4.5,1,'PEOPLE','Missing review gate\nHypothesis'),(7.5,1,'ENVIRONMENT','Thermal change\nNot modeled')]
    for x,y,title,body in branches:
        ax.plot([x+.6,x+1.7],[y,3],color='#64748b',lw=1.5)
        ax.text(x,y+.35 if y>3 else y-.2,title,fontsize=11,weight='bold',color='#1d4ed8',va='bottom' if y>3 else 'top')
        ax.text(x,y-.1 if y>3 else y-.6,body,fontsize=10,va='top',bbox=dict(facecolor='#f8fafc',edgecolor='none',pad=2))
    ax.set_title('NCR-001 | Candidate causes and evidence status',loc='left',fontsize=17,weight='bold',pad=12)
    fig.text(.06,.02,'SIMULATED RCA  |  Only the programmed compensation change is demonstrated.',fontsize=10,color='#475569')
    fig.subplots_adjust(left=.05,right=.97,bottom=.1,top=.86);fig.savefig(target/'fishbone.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(12,4.7));ax.set(xlim=(0,12),ylim=(0,4));ax.axis('off')
    nodes=[('D01','Drawing requirement\n19.70-20.30 mm'),('CP-D01','Recipe + first piece\nFive parts / 15 min'),('IP-D01','Micrometer\nX-bar / R review'),('NCR-001','Signal / hold\n100 challenge parts'),('CA-001','Restore setting\nEffectiveness open')]
    for i,(title,body) in enumerate(nodes):
        x=.1+i*2.4
        ax.add_patch(plt.Rectangle((x,1.3),2.15,1.7,facecolor='#eff6ff',edgecolor='#1d4ed8',lw=1.2))
        ax.text(x+1.075,2.55,title,ha='center',fontsize=13,weight='bold',color='#1d4ed8');ax.text(x+1.075,2.0,body,ha='center',va='center',fontsize=10)
        if i<4:ax.annotate('',xy=(x+2.4,2.15),xytext=(x+2.15,2.15),arrowprops=dict(arrowstyle='->',color='#1d4ed8'))
    ax.set_title('One requirement connects the quality documents',loc='left',fontsize=17,weight='bold')
    ax.text(.1,.7,'Verification: 0 / 200 diameter rejects, with a retained trend alert at subgroup 122.',fontsize=12,color='#14243b')
    fig.text(.06,.03,'SIMULATED QUALITY PLANNING  |  Proposed methods and ownership',fontsize=10,color='#475569')
    fig.subplots_adjust(left=.05,right=.97,bottom=.1,top=.85);fig.savefig(target/'traceability_flow.png',dpi=180);plt.close(fig)

def report(m,g,records,hole):
    out=ROOT/'quality_documents/quality_engineering_case_study.pdf'
    doc=SimpleDocTemplate(str(out),pagesize=(612,792),rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=56,title='Manufacturing Quality Engineering Study',author='Shrey Trivedi')
    cap=m['capability'];story=[]
    story+=page('Manufacturing Quality\nEngineering Study'.replace('\n','<br/>'),'A connected simulation case: inspection integrity, measurement, SPC, corrective action and drawing-based inspection planning.')
    story += [p('Shrey Trivedi | Portfolio edition | September 2026','SubQE'),chart(ROOT/'phase2_spc_capability/charts/01_xbar_r.png'),Spacer(1,8)]
    story += [table([['Phase 1','Phase 2','Inspection exercise'],['20,000 part records<br/>90 GR&R readings','700 ordered records<br/>140 subgroups of five','7 characteristic IDs<br/>1 first-piece record + 2 hole challenges']],[176]*3),Spacer(1,12),p('All production and inspection measurements are synthetic. Minitab execution is pending authenticated access. The later SPC verification contains a trend alert, so corrective-action effectiveness remains open. This packet reports that result without removing the alert.')]
    story.append(PageBreak());story+=page('01 / Case map','One characteristic ID follows the requirement through analysis and reaction.')
    story += [p('Stock -> setup and gage check -> turning -> cross-drilling -> finishing -> first-piece / routine inspection -> disposition','SubQE'),p('D01 shaft diameter connects the Phase 1 inspection audit to the new ordered SPC challenge. H02 hole position is a separate inspection-planning example: the Phase 2 NCR does not claim hole-position measurements.'),table([['Requirement','Planning link','Evidence / reaction'],['D01: 19.70-20.30 mm','CP-D01 / IP-D01 / NCR-001','Frozen-limit alarm; challenge-lot hold; CA-001'],['L01: 49.50-50.50 mm','CP-L01 / IP-L01','Phase 1 length escapes repaired'],['H01/H02: hole size / position','CP-H01/H02 / IP-H01/H02','Bore size + full-axis/bonus example'],['E01/F01/S01: face / form / Ra','CP-E01/F01/S01','Individual method and first-piece record'],['G01: measurement adequacy','CP-G01','Simulated GR&R; physical validation required']],[150,150,228]),Spacer(1,16),p('Evidence boundaries','SubQE'),p('Phase 1 retains its original simulation and repaired inspection logic. Phase 2 is a separate time-ordered experiment. The Rev B drawing is an authored learning addendum to the original Onshape exercise. No physical CMM, shop-floor validation, actual approvals or formal AS9102 experience is asserted.')]
    story.append(PageBreak());story+=page('02 / Measurement and inspection','Keep the existing evidence and understand what it cannot establish.')
    rr=gage_analysis(pd.read_csv(ROOT/'data/gage_rr.csv'))
    story += [table([['Phase 1 result','Interpretation'],['1,067 / 20,000 fail; pass rate 94.665%','Independent diameter and length checks plus assigned defect labels.'],['75 net failures avoided in seed 42','Ideal centering leaves 992 failures; five former oversize labels become other primary defects.'],[f"GR&R SD {rr['grr_sd']:.5f} mm; study variation {rr['percent_study_variation']:.2f}%; ndc {rr['ndc']}",'10 parts x 3 operators x 3 trials. Mixed part range makes the global ratio look favorable.'],['Purpose-specific measurement assessment','Bias, linearity, stability, uncertainty and method suitability remain unverified physically.']],[240,288]),Spacer(1,12),p('Why the new SPC data are separate','SubQE'),p('The 20,000-row dataset did not establish rational subgroups or an actual production sequence. Sorting it by a date field would not repair that limitation. Phase 2 instead defines an explicit sequence, subgroup membership and generator truth.'),p('Phase 2 measurement model','SubQE'),p('True process SD = 0.045 mm; independent measurement SD = 0.006 mm. Observed SD includes both. These are separate authored assumptions, not a transfer of the Phase 1 GR&R result. No measurement-noise subtraction is used for capability.')]
    story.append(PageBreak());story+=page('03 / SPC experiment design','700 observations; five consecutive parts per 15-minute interval.')
    story += [table([['Window','Groups / n','Design purpose'],['Reference','1-40 / 200','Estimate initial limits.'],['Setup challenge','41-60 / 100','Introduce +0.270 mm wrong diameter compensation. All are quarantined challenge data.'],['New baseline','61-100 / 200','Restore setup; estimate revised limits.'],['Verification','101-140 / 200','Apply frozen new limits to later observations.']],[140,105,283]),Spacer(1,12),p('Rules and estimates','SubQE'),p('X-bar: point beyond 3 sigma (T1), nine on one side (T2), six monotonic points (T3). R: beyond-limit T1 only. Runs are marked at their final point. The chart uses Rbar/d2 with d2=2.326, A2=0.576802, D3=0 and D4=2.114.'),p('Five successive part times span four minutes. No unobserved parts are invented for the remaining interval. All windows and seed 20260914 were fixed before looking at output; no points or seeds were selected to create a clean result.'),p('For a live process, the first signal triggers a stop/hold. The complete 20-subgroup challenge window is retrospective training evidence, not permission to keep making suspect parts.')]
    story.append(PageBreak());story+=page('04 / Control charts','The mean shifts while within-subgroup spread remains comparable.')
    story += [chart(ROOT/'phase2_spc_capability/charts/01_xbar_r.png'),Spacer(1,12),table([['Limits','X-bar center / LCL / UCL (mm)','R UCL (mm)'],['Reference',f"{m['reference_limits']['center']:.5f} / {m['reference_limits']['x_lcl']:.5f} / {m['reference_limits']['x_ucl']:.5f}",f"{m['reference_limits']['r_ucl']:.5f}"],['New baseline',f"{m['new_limits']['center']:.5f} / {m['new_limits']['x_lcl']:.5f} / {m['new_limits']['x_ucl']:.5f}",f"{m['new_limits']['r_ucl']:.5f}"]],[95,338,95]),Spacer(1,12),p('All 20 shifted subgroup means signal against the reference limits. Reference and rebaseline have no selected-rule signals. The later verification has one T3 alert; inspect the alarm log and retain the flagged sequence. The model has no new assigned cause in that window, but that knowledge does not justify ignoring a real chart alarm.')]
    story.append(PageBreak());story+=page('05 / Capability with conditions','Specification limits describe acceptance. Control limits describe expected process behavior.')
    story += [chart(ROOT/'phase2_spc_capability/charts/04_capability.png'),table([['Window','Cp','Cpk','Pp','Ppk','Rejects'],*[ [ph.title(),*[f'{cap[ph][k]:.3f}' for k in ['Cp','Cpk','Pp','Ppk']],f"{cap[ph]['failures']}/{cap[ph]['n']}"] for ph in ['reference','setup_shift','rebaseline','verification']]],[138,68,68,68,68,118]),Spacer(1,10),p('Reference and new-baseline estimates follow a no-signal finite-window review. Verification indices are provisional because T3 fired. Shifted indices are descriptive only. Pooled Ppk = '+f"{cap['pooled_invalid']['Ppk']:.3f}"+' mixes distinct means and is not a stable capability claim.')]
    story.append(PageBreak());story+=page('06 / Distribution checks','Normality and independence are assessed, not established by a single p-value.')
    story += [chart(ROOT/'phase2_spc_capability/charts/03_normality.png'),p(f"Reference Shapiro-Wilk p={cap['reference']['shapiro_p']:.3f}; verification p={cap['verification']['shapiro_p']:.3f}. Lag-1 correlations are {cap['reference']['lag1']:.3f} and {cap['verification']['lag1']:.3f}. These diagnostics are consistent with the authored normal-noise model, but do not override chart signals."),p('Within SD is Rbar/d2; overall SD is the sample SD. Cp/Cpk use within variation, Pp/Ppk overall variation. Subgroup sampling noise can make Ppk exceed Cpk in this finite sample; it is not automatically an error.'),p('The verification window has zero diameter failures in 200 parts. Under independent identical Bernoulli trials, its exact one-sided 95% upper bound is 1.487%. Zero observed failures is not a guarantee of zero future failures.')]
    story.append(PageBreak());story+=page('07 / NCR and containment','NCR-001 | D01 | Wrong diameter compensation after setup')
    story += [table([['Field','Simulated record'],['Detection','Subgroup 41, X-bar T1 using frozen reference limits.'],['Affected scope','SPC-041-1 through SPC-060-5; 100 quarantined challenge parts.'],['Nonconforming count','22 measured diameters exceed 20.300 mm.'],['Immediate reaction','Hold lot; preserve setup values and measurements; verify gage before adjustment.'],['Disposition','22 nonconforming pieces await engineering disposition; 78 dimensionally conforming pieces remain held pending review.'],['Responsibility','Proposed: setup technician, manufacturing engineer, quality engineer. No real signatures.']],[135,393]),Spacer(1,14),p('Causal evidence','SubQE'),p('The generator and Setup_Code prove that this model introduced a +0.270 mm diameter shift. Missing recipe comparison and independent first-piece review are hypothetical system-level causes used to design preventive controls. They are not interview findings.'),p('Five Whys','SubQE'),p('High diameter -> wrong compensation -> manual entry without recipe comparison -> no independent first-piece gate -> no assigned release evidence after setup. The first two links are demonstrated by the simulation; the remaining links require real process records before acceptance in a factory.')]
    story.append(PageBreak());story+=page('08 / Root-cause review and action','Separate observed model evidence from alternative hypotheses.')
    story += [table([['Fishbone branch','Candidate cause','Evidence / next check'],['Method','Wrong compensation','Authored +0.270 shift / recipe audit'],['Machine','Tool/holder movement','Not modeled / physical inspection'],['Measurement','Gage zero bias','Noise unchanged in model / reference check'],['Material','Stock change','Not modeled / lot trace'],['People','Missing independent review','Hypothetical / sign-off audit'],['Environment','Temperature change','No Phase 2 thermal shift / collect temperatures']],[105,177,246]),Spacer(1,12),p('CA-001 actions','SubQE'),p('Restore approved setup at subgroup 61; add recipe comparison and first-piece checks to CP-D01; freeze new limits from groups 61-100; evaluate groups 101-140 separately. The restored model removes diameter rejects in the later windows.'),p('Effectiveness is still open','SubQE'),p('The later run has 0/200 failures but one T3 alert. Review that six-point trend and define independent follow-up before real release. Do not reroll the seed, erase points or call this a completed 8D. This retained complication is part of the engineering conclusion.')]
    story.append(PageBreak());story+=page('09 / Datum and tolerance interpretation','Rev B learning addendum: A is the shaft OD axis; B is the seating end.')
    story += [p('The primary cylindrical datum controls transverse translation and tilt. The secondary end face controls axial position. Rotation around the shaft is intentionally free because no cross-hole clocking requirement is assumed. A functional clocking requirement would need additional definition.'),table([['Callout','How to inspect / interpret'],['Basic 25 from B','The exact axial location of the true hole axis; position supplies the tolerance.'],['Position DIA0.10(M) | A | B','A cylindrical zone controlling full-axis location and orientation. At ideal bore size5.02, bonus0.07 gives allowed diameter0.17.'],['B face perpendicularity0.05 | A','Two planes0.05 apart perpendicular to A; evaluate the face in that zone.'],['Cylindricity0.10','Two coaxial cylinders0.10 apart; form control, no datum.'],['Ra <=3.2 micrometres on OD','Profilometer with agreed cutoff/filter/evaluation length; not a visual defect label.']],[200,328]),Spacer(1,12),p('The original Onshape sheet is preserved. Rev B is a separate schematic inspection addendum with intentionally revised datum labels, not an edited native Onshape export. The original labels must not be mixed with this plan. The learning drawing is not released for manufacture.')]
    story.append(PageBreak());story+=page('10 / First-piece inspection record','FP-001 | All values are invented training measurements; no physical inspection performed.')
    story += [table([['ID','Specification','Example result','Decision'],*[ [r['Characteristic'],r['Specification'],f"{r['Simulated_Value']} {r['Unit']}",r['Result']] for r in records]],[45,230,158,95]),Spacer(1,14),p('Hole position challenge records','SubQE'),table([['Record','Actual / allowed zone diameter','Decision'],*[ [r['Record'],f"{r['Position_Diameter_mm']:.3f} / {r['Allowed_Diameter_mm']:.3f} mm",r['Result']] for r in hole]],[140,288,100]),Spacer(1,10),p('The hole example assumes a straight cylindrical axis across20 mm, aligned to the datums and allowed clocking. Maximum endpoint radial error is doubled. Real inspection must include size, form, datum simulation and uncertainty; center coordinates alone cannot validate a tilted bore.')]
    story.append(PageBreak());story+=page('11 / Control-plan linkage','An inspection result must lead to a defined reaction.')
    story += [table([['IDs','Teaching frequency / method','Reaction and evidence'],['D01','First piece; five consecutive/15 min; micrometer + X-bar/R','Hold on any selected-rule alert or size failure; NCR-001 -> CA-001.'],['L01','First piece; after setup; height gage/caliper','Independent limits; segregate; inspect stop/setup.'],['H01/H02','First piece + fixture/tool change; bore + CMM/functional method','Verify size and full axis; hold/NCR on failure.'],['E01/F01','First piece + process change; face/form method','Recheck datum setup, facing/tooling; hold.'],['S01','First piece + tool/finish change; profilometer','Check procedure and finishing; hold.'],['G01','Before adoption + relevant changes; purpose-specific MSA','Physical adequacy required; simulated GR&R alone cannot release method.']],[75,240,213]),Spacer(1,14),p('The full traceability worksheet maps each ID to a failure mode, candidate cause, prevention/detection control, method, reaction and proposed owner. Ratings are deliberately unscored because no team-approved criteria or production evidence exists.'),p('Sampling frequencies are teaching assumptions. This is not an acceptance-sampling plan with demonstrated outgoing quality or a formal FAI approval. Actual roles would review and sign only after physical evidence exists.')]
    story.append(PageBreak());story+=page('12 / Reproduction and remaining work','What is finished, what is conditional, and what still requires access.')
    story += [table([['Deliverable','Status'],['Python SPC and capability','Executed, with exported raw records, subgroup calculations, all alarms and diagnostics.'],['NCR / RCA / control linkage','Complete training documentation; effectiveness remains open by the reported criterion.'],['Drawing / first-piece record','Authored learning addendum and simulated examples; native Onshape revision not performed.'],['Minitab comparison','Prepared inputs, exact options and Python reference; software execution pending sign-in/license.'],['Phase 1','Preserved repaired simulation, GR&R, inspection logic, Excel dashboard and original drawing.']],[160,368]),Spacer(1,14),p('Rebuild','SubQE'),p('Install requirements.txt. Run python scripts/build_quality_package.py, then python scripts/build_spc_notebook.py. Execute python -m unittest discover -s tests -v. CSVs and JSON retain full precision; rounded values on pages are for readability.'),p('Sources','SubQE'),p('NIST: Shewhart X-bar and R charts (itl.nist.gov/div898/handbook/pmc/section3/pmc311.htm); process capability (section1/pmc16.htm). Minitab official documentation: Xbar-R special-cause tests and normal-capability methods. ASME Y14.5 scope and Tec-Ease position interpretation. Full links and option details appear in the Phase2, inspection and Minitab README files. Accessed14 Sep2026.'),p('Resume boundary','SubQE'),p('This release supports discussion of simulated SPC, measurement interpretation, capability conditions, inspection planning and corrective-action documentation. Add Minitab only after completing genuine software runs; keep GD&T qualified as fundamentals / drawing interpretation.')]
    # Standalone diagrams also form two concise visual appendix pages.
    story.append(PageBreak());story+=page('13 / Root-cause map','Hypotheses remain visible beside the demonstrated model cause.')
    story += [chart(ROOT/'quality_documents/fishbone.png'),Spacer(1,14),p('The method branch identifies the programmed compensation error. The other branches identify evidence that a real investigation would collect. They are not claims that alternative physical causes have been ruled out.')]
    story.append(PageBreak());story+=page('14 / Traceability at a glance','From a size requirement to a documented effectiveness decision.')
    story += [chart(ROOT/'quality_documents/traceability_flow.png'),Spacer(1,14),p('Follow D01 through the requirement, prevention/detection control, inspection method, containment record and corrective action. The open effectiveness decision is backed by subgroup122 in the alarm log.')]
    doc.build(story,onFirstPage=footer,onLaterPages=footer)

if __name__=='__main__':
    d,g,m=run();records,hole=inspection();minitab(d,m);drawing();diagrams();report(m,g,records,hole)
    print('Built quality packet, learning drawing, inspection examples and Minitab import/reference files.')
