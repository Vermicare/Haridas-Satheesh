import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {auditExistingPrivateUpstoxDevelopment}
  from './reaudit_existing_private_upstox.mjs';

const day='2025-01-06';
const sha=buffer=>crypto.createHash('sha256').update(buffer).digest('hex');
const folder=t=>{
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'qhap-upstox-reaudit-'));
  t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
  return root;
};
const makeRows=({opening=true}={})=>{
  const lines=[];
  for(let m=opening?555:556;m<=929;m++){
    const time=String(Math.floor(m/60)).padStart(2,'0')+':'+
      String(m%60).padStart(2,'0');
    lines.push(['RELIANCE','20250106',time,'100.00','100.40',
      '99.70','100.20','100','0'].join(','));
  }
  return lines.join('\n')+'\n';
};
function writeFixture(root,{opening=true,hashOverride=null,state=
  'CANDIDATE_COMPLETE_UNVERIFIED',writeSource=true}={}){
  const source=makeRows({opening});
  const csv=path.join(root,'historical','2025','01','06','RELIANCE.csv');
  fs.mkdirSync(path.dirname(csv),{recursive:true});
  if(writeSource)fs.writeFileSync(csv,source);
  const auditPath=path.join(root,'manifests',
    'development-RELIANCE-2025-01-06-to-2025-01-10.audit.json');
  fs.mkdirSync(path.dirname(auditPath),{recursive:true});
  const doc={
    kind:'QHAP_LOCAL_DEVELOPMENT_ONLY_UNVERIFIED',
    dataSource:'Upstox Historical Candle V3 one-minute NSE_EQ',
    requestedFrom:'2025-01-06',requestedTo:'2025-01-10',
    perDay:[{date:day,symbol:'RELIANCE',minuteBars:opening?375:374,
      candidateState:state,sha256:hashOverride||sha(source)}]
  };
  fs.writeFileSync(auditPath,JSON.stringify(doc));
  return {source,csv,auditPath};
}
test('no local audit files means NO DATA, not a false complete session',t=>{
  const root=folder(t);
  const x=auditExistingPrivateUpstoxDevelopment(root);
  assert.equal(x.status,'NO_EXISTING_PRIVATE_UPSTOX_AUDITS_FOUND_NO_TRADE');
  assert.equal(x.archivedSessionsExamined,0);
  assert.equal(x.realOrdersSent,0);
});
test('legacy candidate with 374 minutes missing 09:15 is downgraded',t=>{
  const root=folder(t);writeFixture(root,{opening:false});
  const x=auditExistingPrivateUpstoxDevelopment(root);
  assert.equal(x.archivedSessionsExamined,1);
  assert.equal(x.previouslyLabeledCandidates,1);
  assert.equal(x.staleCandidateLabels,1);
  assert.equal(x.missingOpeningCandidates,1);
  assert.deepEqual(x.affectedCandidateDates,[{date:day,
    reason:'MISSING_09_15_OPEN'}]);
  assert.equal(x.previouslyLabeledCandidatesPassingFull375Shape,0);
  assert.equal(x.filesModified,0);
  assert.equal(x.networkRequestsMade,0);
  assert.equal(x.canTrade,false);
});
test('375 proper minute bars passes structure without trading evidence',t=>{
  const root=folder(t);writeFixture(root);
  const x=auditExistingPrivateUpstoxDevelopment(root);
  assert.equal(x.status,'ARCHIVED_UPSTOX_DEVELOPMENT_STRUCTURE_RECHECKED_NO_TRADE');
  assert.equal(x.previouslyLabeledCandidatesPassingFull375Shape,1);
  assert.equal(x.staleCandidateLabels,0);
  assert.equal(x.genuineUnseenHoldoutSessions,0);
  assert.equal(x.sourceRightsIndependentlyVerified,false);
  assert.equal(x.calendarsIndependentlyVerified,false);
});
test('source tampering is detected via original private SHA-256',t=>{
  const root=folder(t);writeFixture(root,{hashOverride:'a'.repeat(64)});
  const x=auditExistingPrivateUpstoxDevelopment(root);
  assert.equal(x.staleCandidateLabels,1);
  assert.equal(x.missingOrModifiedPrivateSourceFiles,1);
  assert.equal(x.affectedCandidateDates[0].reason,
    'MISSING_OR_HASH_MISMATCHED_SOURCE');
});
test('missing private CSV never counted as a complete source day',t=>{
  const root=folder(t);writeFixture(root,{writeSource:false});
  const x=auditExistingPrivateUpstoxDevelopment(root);
  assert.equal(x.missingOrModifiedPrivateSourceFiles,1);
  assert.equal(x.previouslyLabeledCandidatesPassingFull375Shape,0);
});
test('prior excluded day stays excluded, never newly promoted',t=>{
  const root=folder(t);writeFixture(root,{opening:false,writeSource:false,
    state:'INCOMPLETE_MINUTE_COVERAGE'});
  const x=auditExistingPrivateUpstoxDevelopment(root);
  assert.equal(x.priorExcludedSessionsUntouched,1);
  assert.equal(x.previouslyLabeledCandidates,0);
  assert.equal(x.filesModified,0);
});
test('malformed audit metadata is rejected without visiting unsafe source path',t=>{
  const root=folder(t);
  const {auditPath}=writeFixture(root);
  const doc=JSON.parse(fs.readFileSync(auditPath,'utf8'));
  doc.perDay[0].symbol='../../secret';
  fs.writeFileSync(auditPath,JSON.stringify(doc));
  const x=auditExistingPrivateUpstoxDevelopment(root);
  assert.equal(x.invalidAuditFiles,1);
  assert.equal(x.archivedSessionsExamined,0);
  assert.equal(x.previouslyLabeledCandidatesPassingFull375Shape,0);
});
test('read-only CLI output is aggregate-only and leaves bytes unchanged',t=>{
  const root=folder(t);
  const {source,csv,auditPath}=writeFixture(root,{opening:false});
  // CLI always uses user's home. Run the injected function to avoid touching
  // actual user-local data, and inspect module for credential/network routes.
  const a=fs.readFileSync(csv,'utf8'),b=fs.readFileSync(auditPath,'utf8');
  const out=JSON.stringify(auditExistingPrivateUpstoxDevelopment(root));
  assert.equal(fs.readFileSync(csv,'utf8'),a);
  assert.equal(fs.readFileSync(auditPath,'utf8'),b);
  for(const item of ['100.00','99.70','100.20',csv,auditPath,
    'access_token','authorization','"candles"']){
    assert.equal(out.includes(item),false,item);
  }
  assert.equal(source.length>0,true);
  const code=fs.readFileSync(new URL('./reaudit_existing_private_upstox.mjs',
    import.meta.url),'utf8');
  for(const forbidden of ['fetch(', 'WebSocket(', 'createOrder(',
    'placeOrder(', 'axios(', 'process.env.UPSTOX_ANALYTICS_TOKEN']){
    assert.equal(code.includes(forbidden),false,forbidden);
  }
});
