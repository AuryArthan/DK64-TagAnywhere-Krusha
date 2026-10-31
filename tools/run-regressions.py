#!/usr/bin/python3
"""Run focused regressions sequentially in a new, exact-ROM profile."""
from pathlib import Path
import os,subprocess,json,hashlib,time,shutil
ROOT=Path(__file__).resolve().parent.parent
OUT=Path(os.environ['DK64_QA_OUT']).resolve()
if OUT.exists() and any(OUT.iterdir()) and not os.environ.get('DK64_REGRESSION_STAGES'):
 raise SystemExit('Choose a new empty DK64_QA_OUT directory to preserve previous results.')
OUT.mkdir(parents=True,exist_ok=True)
PROFILE=OUT/'profile';env={**os.environ,'DK64_RUNTIME':str(PROFILE)}
stages=[('core','krusha-test.py','ALL_CHECKS_COMPLETE','krusha-tests.json'),
 ('extra','krusha-extra-test.py','EXTRA_CHECKS_COMPLETE','krusha-extra-tests.json'),
 ('barrel','krusha-barrel-test.py','BARREL_CHECKS_COMPLETE','krusha-barrel-tests.json'),
 ('gun','krusha-v2-test.py','GUN_AND_BARREL_CHECKS_COMPLETE','krusha-v2-tests.json'),
 ('barrel-extra','krusha-barrel-extra-test.py','BARREL_EXTRA_CHECKS_COMPLETE','krusha-barrel-extra-tests.json'),
 ('options','krusha-options-test.py','OPTIONS_CHECKS_COMPLETE','krusha-options-tests.json')]
summary={'rom_sha256':hashlib.sha256((ROOT/'rom/dk64-krusha-dev.z64').read_bytes()).hexdigest(),'stages':[]}
selected=os.environ.get('DK64_REGRESSION_STAGES')
if selected:
 stages=[s for s in stages if s[0] in selected.split(',')]
 old=json.loads((OUT/'summary.json').read_text());assert old['rom_sha256']==summary['rom_sha256']
 summary['stages']=[r for r in old['stages'] if r['stage'] not in selected.split(',')]
try:
 for name,script,marker,report in stages:
  log=OUT/(name+'.log');print('START',name,flush=True)
  with log.open('w') as f:
   p=subprocess.run(['/usr/bin/python3','-u',str(ROOT/'tools'/script)],cwd=ROOT,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,timeout=1200)
  source=PROFILE/'logs'/report
  if not source.exists():raise AssertionError(name+' missing report')
  result=json.loads(source.read_text());shutil.copy2(source,OUT/(name+'-checks.json'))
  good=p.returncode==0 and result.get('complete') and result['rom_sha256']==summary['rom_sha256'] and all(c['passed'] for c in result['checks'])
  row={'stage':name,'complete':bool(good),'assertions':len(result['checks']),'error':result.get('error')};summary['stages'].append(row);print(json.dumps(row),flush=True)
  (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
  if not good:raise AssertionError(name+' failed')
 summary['complete']=True
except Exception as e:summary['error']=repr(e);print('REGRESSION_ERROR',repr(e),flush=True)
finally:(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print('REGRESSION_COMPLETE',summary.get('complete'),flush=True)
