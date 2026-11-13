#!/usr/bin/env node
/**
 * REAUDIT IMMUTABLE user-local Upstox development sessions after the 09:15
 * coverage fix. No network, broker access, tokens, orders, data downloads,
 * archive mutation or raw price output. Never promote to unseen holdout.
 */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parseCompleteSession} from '../experiments/intraday_clock_replay.mjs';

const HOME=()=>path.join(os.homedir(),'QHAP-TRADER-PRIVATE');
const AUDIT_NAME=/^development-([A-Z][A-Z0-9&_-]{0,20})-(20\d{2}-\d{2}-\d{2})-to-(20\d{2}-\d{2}-\d{2})\.audit\.json$/;
const SYMBOL=/^[A-Z][A-Z0-9&_-]{0,20}$/;
const HASH=/^[a-f0-9]{64}$/;
const ONE_FILE_MAX=5_000_000;
const MAX_AUDIT_FILES=400;
const MAX_DAYS=6000;
const sha=raw=>crypto.createHash('sha256').update(raw).digest('hex');
const validDate=d=>{
  if(typeof d!=='string'||!/^20\d{2}-\d{2}-\d{2}$/.test(d))return false;
  const ms=Date.parse(d+'T00:00:00Z');
  return Number.isFinite(ms)&&new Date(ms).toISOString().slice(0,10)===d;
};
const resultBase=()=>({
  status:'PRIVATE_UPSTOX_REAUDIT_NOT_YET_COMPLETE_NO_TRADE',
  researchClassification:'INSPECTED_PRIVATE_DEVELOPMENT_NOT_FROZEN_HOLDOUT',
  localOnly:true,readOnly:true,networkRequestsMade:0,
  credentialsRead:false,filesModified:0,realOrdersSent:0,paperOrdersSent:0,
  brokerOrderRoutePresent:false,canTrade:false,canMakeEdgeClaims:false,
  finalBrokerDecision:'NO_TRADE',
  calendarsIndependentlyVerified:false,sourceRightsIndependentlyVerified:false,
  genuineUnseenHoldoutSessions:0,
  auditFilesExamined:0,invalidAuditFiles:0,
  archivedSessionsExamined:0,previouslyLabeledCandidates:0,
  previouslyLabeledCandidatesPassingFull375Shape:0,
  staleCandidateLabels:0,missingOpeningCandidates:0,
  otherRejectedCandidates:0,priorExcludedSessionsUntouched:0,
  missingOrModifiedPrivateSourceFiles:0,
  duplicatedAuditSessionReferences:0,
  affectedCandidateDates:[],
  rawSourceCandlesPrinted:false
});
function localFileBytes(file,root){
  // The private root is supplied only by local CLI default or a test injection.
  const rootReal=fs.realpathSync(root);
  const real=fs.realpathSync(file);
  if(!real.startsWith(rootReal+path.sep))throw Error('OUTSIDE_PRIVATE_ROOT');
  const stat=fs.lstatSync(file);
  if(!stat.isFile()||stat.isSymbolicLink()||stat.size<2||stat.size>ONE_FILE_MAX)
    throw Error('INVALID_LOCAL_FILE');
  const raw=fs.readFileSync(file);
  if(raw.byteLength!==stat.size)throw Error('INCONSISTENT_LOCAL_READ');
  return raw;
}
const validEntry=(entry,from,to,symbol)=>entry&&
  Object.keys(entry).length>=4&&validDate(entry.date)&&
  entry.date>=from&&entry.date<=to&&entry.symbol===symbol&&
  SYMBOL.test(entry.symbol)&&HASH.test(entry.sha256||'')&&
  typeof entry.candidateState==='string';
export function auditExistingPrivateUpstoxDevelopment(privateRoot=HOME()){
  const out=resultBase();
  if(typeof privateRoot!=='string'||!path.isAbsolute(privateRoot))
    throw Error('PRIVATE_ROOT_REQUIRED');
  const manifestRoot=path.join(privateRoot,'manifests');
  if(!fs.existsSync(manifestRoot)){
    return {...out,status:'NO_EXISTING_PRIVATE_UPSTOX_AUDITS_FOUND_NO_TRADE'};
  }
  let files;
  try{
    files=fs.readdirSync(manifestRoot,{withFileTypes:true})
      .filter(x=>x.name.endsWith('.audit.json'))
      .map(x=>({name:x.name,regular:x.isFile()}))
      .sort((a,b)=>a.name.localeCompare(b.name));
  }catch{throw Error('LOCAL_AUDIT_DIRECTORY_UNREADABLE');}
  if(files.length>MAX_AUDIT_FILES)throw Error('TOO_MANY_LOCAL_AUDIT_FILES');
  if(!files.length){
    return {...out,status:'NO_EXISTING_PRIVATE_UPSTOX_AUDITS_FOUND_NO_TRADE'};
  }
  const seen=new Set();
  for(const file of files){
    out.auditFilesExamined++;
    const m=AUDIT_NAME.exec(file.name);
    if(!m||!file.regular){out.invalidAuditFiles++;continue;}
    let doc;
    try{
      doc=JSON.parse(localFileBytes(path.join(manifestRoot,file.name),
        privateRoot).toString('utf8'));
    }catch{out.invalidAuditFiles++;continue;}
    if(!doc||doc.kind!=='QHAP_LOCAL_DEVELOPMENT_ONLY_UNVERIFIED'||
      doc.requestedFrom!==m[2]||doc.requestedTo!==m[3]||
      !Array.isArray(doc.perDay)||doc.perDay.length>31){
      out.invalidAuditFiles++;continue;
    }
    for(const entry of doc.perDay){
      if(out.archivedSessionsExamined>=MAX_DAYS)
        throw Error('TOO_MANY_LOCAL_SESSIONS');
      if(!validEntry(entry,m[2],m[3],m[1])){
        out.invalidAuditFiles++;continue;
      }
      const key=entry.symbol+'|'+entry.date;
      if(seen.has(key)){out.duplicatedAuditSessionReferences++;continue;}
      seen.add(key);
      out.archivedSessionsExamined++;
      const oldCandidate=entry.candidateState==='CANDIDATE_COMPLETE_UNVERIFIED';
      if(!oldCandidate){out.priorExcludedSessionsUntouched++;continue;}
      out.previouslyLabeledCandidates++;
      const ymd=entry.date.replaceAll('-','');
      const csvFile=path.join(privateRoot,'historical',
        entry.date.slice(0,4),entry.date.slice(5,7),
        entry.date.slice(8,10),entry.symbol+'.csv');
      let source;
      try{
        source=localFileBytes(csvFile,privateRoot);
        if(sha(source)!==entry.sha256)throw Error('SOURCE_HASH_MISMATCH');
      }catch{
        out.missingOrModifiedPrivateSourceFiles++;
        out.staleCandidateLabels++;
        if(out.affectedCandidateDates.length<50)
          out.affectedCandidateDates.push({date:entry.date,
            reason:'MISSING_OR_HASH_MISMATCHED_SOURCE'});
        continue;
      }
      try{
        parseCompleteSession(source.toString('utf8'),entry.symbol,ymd);
        out.previouslyLabeledCandidatesPassingFull375Shape++;
      }catch(error){
        out.staleCandidateLabels++;
        const missingOpening=error?.message==='MISSING_OPENING_MINUTE_09_15';
        if(missingOpening)out.missingOpeningCandidates++;
        else out.otherRejectedCandidates++;
        if(out.affectedCandidateDates.length<50)
          out.affectedCandidateDates.push({date:entry.date,
            reason:missingOpening?'MISSING_09_15_OPEN':'INVALID_OR_PARTIAL_SESSION'});
      }
    }
  }
  out.status=out.invalidAuditFiles||
    out.missingOrModifiedPrivateSourceFiles||out.duplicatedAuditSessionReferences||
    out.staleCandidateLabels?
    'ARCHIVED_UPSTOX_DEVELOPMENT_CANDIDATES_REQUIRE_REVIEW_NO_TRADE':
    'ARCHIVED_UPSTOX_DEVELOPMENT_STRUCTURE_RECHECKED_NO_TRADE';
  return out;
}
const invoked=process.argv[1]&&
  path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(invoked){
  try{
    if(process.argv.length!==3||process.argv[2]!=='--audit-local')
      throw Error('USE_AUDIT_LOCAL_ONLY');
    console.log(JSON.stringify(auditExistingPrivateUpstoxDevelopment(),null,2));
  }catch{
    console.error(JSON.stringify({
      status:'PRIVATE_UPSTOX_REAUDIT_HALTED_NO_TRADE',
      reason:'LOCAL_SOURCE_OR_AUDIT_INSPECTION_FAILED',
      canTrade:false,realOrdersSent:0,networkRequestsMade:0,
      rawSourceCandlesPrinted:false
    }));
    process.exitCode=1;
  }
}
