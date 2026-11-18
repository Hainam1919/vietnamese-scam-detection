"""Read-only dataset audit for the SIC report; does not retrain or edit CSVs."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from train import read_split
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
 result={};frames={}
 for name in ['train','test']:
  path=ROOT/'data'/f'{name}.csv';raw=pd.read_csv(path);d=read_split(path);frames[name]=d;n=d.message.str.len()
  result[name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'raw_rows':len(raw),'usable_rows':len(d),'null_message':int(raw.message.isna().sum()),'null_label':int(raw.label.isna().sum()),'duplicate_message':int(d.message.duplicated().sum()),'class_counts':{str(k):int(v) for k,v in d.label.value_counts().items()},'length_chars':{'min':int(n.min()),'median':float(n.median()),'mean':round(float(n.mean()),1),'max':int(n.max())}}
 a,b=frames['train'],frames['test'];result['exact_overlap_unique']=len(set(a.message)&set(b.message))
 norm=lambda x:x.str.lower().str.replace(r'\s+',' ',regex=True)
 result['normalized_overlap_unique']=len(set(norm(a.message))&set(norm(b.message)))
 result['exact_overlap_test_rows']=int(b.message.isin(set(a.message)).sum())
 result['note']='Duplicates count rows after the first occurrence. Cross-split overlap counts unique contents. No semantic/near-duplicate audit or retraining performed.'
 out=ROOT/'reports'/'sic_data_audit.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2));print(out)
if __name__=='__main__':main()
