import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(process.env.ARTIFACT_TOOL_RESOLVE_FROM || import.meta.url);
const {Workbook,SpreadsheetFile}=await import(require.resolve('@oai/artifact-tool'));
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const m=JSON.parse(await fs.readFile(path.join(root,'dashboard/metrics.json'),'utf8'));
const rows=JSON.parse(await fs.readFile(path.join(root,'results/workbook_rows.json'),'utf8'));
const w=Workbook.create(),s=w.worksheets.add('Dashboard'),d=w.worksheets.add('Data');
const n=rows.length+5, end=n;
const navy='#203343',blue='#28647A',gray='#63737D';
for(const sh of [s,d]){sh.showGridLines=false;sh.getRange(sh===s?'A1:N67':`A1:I${n}`).format.font={name:'Arial',size:11};}
s.getRange('A1:N67').format.columnWidth=12;s.getRange('A1:N67').format.rowHeight=23;
s.getRange('A2').values=[['Machining inspection and centering']];s.getRange('A2').format.font={name:'Arial',size:17,bold:true,color:navy};
s.getRange('A3').values=[['Simulated data. Baseline inspection includes diameter, length and assigned primary defects.']];
const head=(range)=>{s.getRange(range).format.fill=navy;s.getRange(range).format.font={name:'Arial',size:11,bold:true,color:'#FFFFFF'};};
for(const [r,text,formula,fmt] of [['A5','Inspected parts',`COUNTA('Data'!A6:A${end})`,'#,##0'],['D5','Failed parts',`SUM('Data'!G6:G${end})`,'#,##0'],['G5','Pass rate','1-D6/A6','0.000%'],['J5','PPM defective','D6/A6*1000000','#,##0']]){
 s.getRange(r).values=[[text]];s.getRange(r).format.font={name:'Arial',size:11,color:gray,bold:true};let a=r.replace('5','6');s.getRange(a).formulas=[['='+formula]];s.getRange(a).setNumberFormat(fmt);s.getRange(a).format.font={name:'Arial',size:17,bold:true,color:navy};
}
s.getRange('A9:D9').values=[['Machine','Parts','Failures','Failure rate']];head('A9:D9');
for(let i=0;i<4;i++){let r=i+10;s.getRange(`A${r}`).values=[['M'+(i+1)]];s.getRange(`B${r}:D${r}`).formulas=[[`=COUNTIFS('Data'!B$6:B$${end},A${r})`,`=SUMIFS('Data'!G$6:G$${end},'Data'!B$6:B$${end},A${r})`,`=C${r}/B${r}`]];}
s.getRange('D10:D13').setNumberFormat('0.00%');
s.getRange('G9:J9').values=[['Primary defect','Count','Share','Cumulative']];head('G9:J9');
const cats=Object.keys(m.primary_defects);
cats.forEach((cat,i)=>{let r=10+i;s.getRange(`G${r}`).values=[[cat]];s.getRange(`H${r}:J${r}`).formulas=[[`=COUNTIFS('Data'!F$6:F$${end},G${r})`,`=H${r}/D$6`,`=SUM(I$10:I${r})`]];});
s.getRange('G9:G15').format.columnWidth=20;s.getRange('I10:J15').setNumberFormat('0.0%');
s.getRange('A15').values=[['Diameter failures']];s.getRange('C15').formulas=[[`=SUM('Data'!H6:H${end})`]];
s.getRange('A16').values=[['Length failures']];s.getRange('C16').formulas=[[`=SUM('Data'!I6:I${end})`]];
s.getRange('A18').values=[['Characteristic failure counts can overlap. Primary categories count each failed part once.']];
function chart(ranges,title,start,finish,format){let c=s.charts.add('bar',ranges.map(r=>s.getRange(r)));c.title=title;c.titleTextStyle.fontSize=14;c.titleTextStyle.typeface='Arial';c.setPosition(start,finish);c.hasLegend=false;c.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:11}};c.yAxis={numberFormatCode:format,numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:11}};for(const series of c.series.items)series.fill=blue;return c;}
chart(['A9:A13','D9:D13'],'Inspection failure rate by machine','A20','G34','0%');
chart(['G9:G15','H9:H15'],'Primary failure categories (parts)','H20','N34','#,##0');
s.getRange('A36').values=[['Paired simulation: ideal centering, seed 42']];s.getRange('A36').format.font={name:'Arial',size:14,bold:true};
s.getRange('A38:F38').values=[['Scenario','Parts','Failures','Pass rate','Diameter fails','Length fails']];head('A38:F38');
for(const [r,key,label] of [[39,'baseline','Baseline'],[40,'centered','Centered']]){let q=m[key];s.getRange(`A${r}:F${r}`).values=[[label,q.parts,q.failures,null,q.diameter_failures,q.length_failures]];s.getRange(`D${r}`).formulas=[[`=1-C${r}/B${r}`]];}
s.getRange('D39:D40').setNumberFormat('0.000%');s.getRange('A42').values=[['Net failures avoided']];s.getRange('C42').formulas=[['=C39-C40']];
s.getRange('A44').values=[['Scenario counts are outputs of the generator, not a live factory forecast or measured savings.']];
s.getRange('A46').values=[['Simulated crossed Gage R&R']];s.getRange('A46').format.font={name:'Arial',size:14,bold:true};
s.getRange('A48').values=[['Gage SD (mm)']];s.getRange('C48').values=[[m.gage.grr_sd]];
s.getRange('E48').values=[['% study variation']];s.getRange('G48').values=[[m.gage.percent_study_variation/100]];
s.getRange('A49').values=[['% tolerance']];s.getRange('C49').values=[[m.gage.percent_tolerance/100]];
s.getRange('E49').values=[['Distinct categories']];s.getRange('G49').values=[[m.gage.ndc]];
s.getRange('A50').values=[['Design: 10 parts x 3 operators x 3 trials']];
s.getRange('C48').setNumberFormat('0.00000');s.getRange('G48').setNumberFormat('0.00%');s.getRange('C49').setNumberFormat('0.00%');
s.getRange('A52').values=[['These estimates describe the selected simulated parts, not approval of a physical gage.']];
s.getRange('A54').values=[['Refresh: python scripts/rebuild.py, then python scripts/rebuild_excel_local.py (bundled runtime).']];
s.getRange('A55').values=[['The rebuild imports the complete corrected CSV. Excel formulas summarize the prepared Data rows.']];
s.getRange('A56').values=[['Changing only a measurement cell does not rerun the inspection model. Rebuild from the CSV.']];
s.getRange('A57').values=[['Scenario and GR&R outputs refresh during rebuild; they do not recalculate from Excel edits.']];
d.getRange('A2').values=[['Prepared observations from data/manufacturing.csv']];d.getRange('A2').format.font={name:'Arial',size:15,bold:true};
d.getRange('A3').values=[['Generated simulation, seed 42. Flags are 0/1. Full source hash appears in dashboard/metrics.json.']];
d.getRange('A5:I5').values=[['Part ID','Machine','Shift','Diameter (mm)','Length (mm)','Primary defect','Failed','Diameter fail','Length fail']];
d.getRange(`A6:I${end}`).values=rows;
d.getRange(`A5:I${end}`).format.columnWidth=16;d.getRange(`F5:F${end}`).format.columnWidth=22;
d.getRange('A5:I5').format.fill=navy;d.getRange('A5:I5').format.font={name:'Arial',size:11,bold:true,color:'#FFFFFF'};
d.getRange(`D6:E${end}`).setNumberFormat('0.00000');d.freezePanes.freezeRows(5);
w.recalculate();
const val=(a)=>s.getRange(a).values[0][0];
for(const [a,expected] of [['A6',m.baseline.parts],['D6',m.baseline.failures],['C15',m.baseline.diameter_failures],['C16',m.baseline.length_failures],['C42',m.baseline.failures-m.centered.failures]])if(Math.abs(val(a)-expected)>1e-8)throw Error(`Mismatch ${a}: ${val(a)} vs ${expected}`);
// Reversible in-memory mutation verifies formula dependency on row-level flags.
const original=d.getRange('G6').values[0][0];d.getRange('G6').values=[[1-original]];w.recalculate();
if(val('D6')!==m.baseline.failures+1-2*original)throw Error('Dashboard dependency test failed');
d.getRange('G6').values=[[original]];w.recalculate();
const errors=await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:20},maxChars:2000});console.log(errors.ndjson);
await (await SpreadsheetFile.exportXlsx(w)).save(path.join(root,'dashboard/quality_dashboard.xlsx'));
if(process.env.DASHBOARD_QA_DIR){
 await fs.mkdir(process.env.DASHBOARD_QA_DIR,{recursive:true});
 for(const [sheetName,range,name] of [['Dashboard','A1:N34','dashboard-top'],['Dashboard','A36:N58','dashboard-detail'],['Data','A1:I18','data']]){
  const p=await w.render({sheetName,range,scale:1.3});await fs.writeFile(path.join(process.env.DASHBOARD_QA_DIR,name+'.png'),new Uint8Array(await p.arrayBuffer()));
 }
}
console.log('Workbook exported; headline reconciliation and row-level dependency test passed.');
