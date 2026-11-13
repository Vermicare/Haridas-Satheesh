#!/usr/bin/env node
/**
 * QHAP-TRADER local OFFLINE engineering readiness command.
 * Runs existing Node test suites with an allowlisted, credential-free
 * environment; never downloads exchange prices, connects to brokers,
 * evaluates real trades or changes actual/virtual account state.
 *
 * A passing test suite means SOFTWARE INVARIANTS passed ONLY. It is not
 * external market-data entitlement, broker authorization or strategy edge.
 */
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {assessLiveReadinessInventory} from './readiness_gate.mjs';

export const SUITE_NAMES=Object.freeze([
  'LIVE_READINESS_OFFLINE_INVARIANTS',
  'GUARDED_HISTORICAL_OFFLINE_INVARIANTS',
  'ILLUSTRATIVE_FEE_FORMULA_INVARIANTS'
]);
const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../../..');
const experiments=path.resolve(root,'projects/qhap-trader/experiments');
const toRelative=p=>path.relative(root,p).split(path.sep).join('/');
const safeEnv=()=>Object.fromEntries(
  ['PATH','Path','SystemRoot','SYSTEMROOT','HOME','TMP','TEMP','TMPDIR','USERPROFILE']
    .filter(k=>typeof process.env[k]==='string')
    .map(k=>[k,process.env[k]])
);
const summaryLines=text=>{
  const tests=[...text.matchAll(/^# tests (\d+)$/gm)];
  const passes=[...text.matchAll(/^# pass (\d+)$/gm)];
  const fails=[...text.matchAll(/^# fail (\d+)$/gm)];
  return tests.length&&passes.length&&fails.length?
    {tests:Number(tests.at(-1)[1]),passed:Number(passes.at(-1)[1]),
      failed:Number(fails.at(-1)[1])}:null;
};
const validSuite=r=>r&&typeof r==='object'&&r.status==='PASSED'&&
  Number.isSafeInteger(r.tests)&&r.tests>0&&
  r.passed===r.tests&&r.failed===0&&r.exitCode===0;
const val={marketDataUseRights:'NOT_INDEPENDENTLY_VERIFIED',
  unseenMultiRegimeNetEdge:'NOT_INDEPENDENTLY_VERIFIED',
  genuineForwardSessions:'NOT_INDEPENDENTLY_VERIFIED',
  brokerAccountAndExecutionPermissions:'NOT_INDEPENDENTLY_VERIFIED',
  regulatoryAndHumanRelease:'NOT_APPROVED'};

/** Decisions never accept caller supplied license/trading booleans. */
export function summarizeOfflineReleasePreflight(suites){
  const names=SUITE_NAMES;
  const valid=Array.isArray(suites)&&suites.length===names.length&&
    names.every(name=>suites.filter(x=>x?.name===name).length===1);
  const passed=valid&&suites.every(validSuite);
  const inventory=assessLiveReadinessInventory();
  return {
    status:passed?'ENGINEERING_OFFLINE_CHECKS_PASSED_EXTERNAL_GATES_OPEN':
      'ENGINEERING_OFFLINE_CHECKS_FAILED_NO_TRADE',
    mode:'LOCAL_TEST_ONLY_NO_LIVE_OR_PAPER_DATA_STREAMS',
    testsPassed:passed,
    testCount:valid?suites.reduce((a,x)=>a+(Number.isSafeInteger(x.tests)?x.tests:0),0):null,
    suites:Array.isArray(suites)?suites:[],
    externalGates:{...val},
    reviewItemsRequired:inventory.itemsRequired,
    reviewItemsClaimed:inventory.itemsClaimed,
    netProfitableStrategyIndependentlyVerified:false,
    marketDataResearchLicenceIndependentlyVerified:false,
    liveFeedVirtualTradingRightsIndependentlyVerified:false,
    brokerOrderEndpointPresent:false,
    realOrderSubmissionPossible:false,
    liveTradingAuthorized:false,
    realOrdersSent:0,
    canTrade:false,
    recommendedAction:'NO_TRADE',
    nextAction:passed?'OBTAIN_WRITTEN_USE_RIGHTS_AND_FROZEN_UNSEEN_NET_COSTED_EVIDENCE':
      'FIX_FAILED_LOCAL_INVARIANTS_BEFORE_ANY_ADDITIONAL_RESEARCH',
    explanation:'Passing tests does not authenticate NSE market data, broker accounts, statutory fees, valid live fills, statistical edge, or human compliance approval.'
  };
}
function runNode(args,label,matcher){
  const processResult=spawnSync(process.execPath,args,{
    cwd:root,env:safeEnv(),encoding:'utf8',shell:false,
    timeout:120000,maxBuffer:3*1024*1024,windowsHide:true
  });
  const stdout=processResult.stdout||'';
  const parsed=matcher(stdout);
  const passed=!processResult.error&&processResult.status===0&&
    parsed&&parsed.tests>0&&parsed.failed===0&&parsed.passed===parsed.tests;
  return {name:label,status:passed?'PASSED':'FAILED',
    exitCode:processResult.status,
    tests:parsed?.tests??0,passed:parsed?.passed??0,failed:parsed?.failed??1,
    didTimeOut:processResult.error?.code==='ETIMEDOUT',
    noNetwork:true,noBrokerCredentialsPassed:true};
}
export function runLocalEngineeringPreflight(){
  let tests;
  try{
    tests=fs.readdirSync(here).filter(x=>/^test_.*\.mjs$/.test(x))
      .map(x=>toRelative(path.join(here,x))).sort();
  }catch{tests=[];}
  const first=tests.length?
    runNode(['--test',...tests],SUITE_NAMES[0],summaryLines):
    {name:SUITE_NAMES[0],status:'FAILED',exitCode:null,tests:0,
      passed:0,failed:1};
  const second=runNode(['--test',
    toRelative(path.join(experiments,'test_costed_intraday_pilot.mjs')),
    toRelative(path.join(experiments,'test_guarded_paper_replay.mjs')),
    toRelative(path.join(experiments,'feb2021_calendar_gate.test.mjs'))],
    SUITE_NAMES[1],summaryLines);
  const third=runNode([
    toRelative(path.join(experiments,'test_fee_formula_audit.mjs'))],
    SUITE_NAMES[2],output=>{
      const p=output.match(/(^|\n)(\d+)\/(\d+) synthetic fee tests passed;/);
      return p?{tests:Number(p[3]),passed:Number(p[2]),failed:0}:null;
    });
  return summarizeOfflineReleasePreflight([first,second,third]);
}
const invoked=process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(invoked){
  if(process.argv.length!==3||!['--offline-check','--help'].includes(process.argv[2])){
    console.error('Usage: node projects/qhap-trader/live_readiness/operator_offline_preflight.mjs --offline-check | --help');
    process.exitCode=2;
  }else if(process.argv[2]==='--help'){
    console.log('OFFLINE ONLY: --offline-check runs local QHAP software tests. Green tests NEVER enable broker orders or authorize market-data use.');
  }else{
    const result=runLocalEngineeringPreflight();
    console.log(JSON.stringify(result,null,2));
    // 0 acknowledges green ENGINEERING TESTS ONLY, never live authorization.
    process.exitCode=result.testsPassed?0:1;
  }
}
