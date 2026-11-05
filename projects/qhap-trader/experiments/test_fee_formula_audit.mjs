#!/usr/bin/env node
// Offline regression checks of the ACTUAL committed fee closure, not a reimplementation.
// Research-only: no network, market data, brokerage, or trading.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const source=fs.readFileSync(new URL('./costed_intraday_pilot.mjs',import.meta.url),'utf8');
const start=source.indexOf('  const fees=(buy,sell,qty)=>{');
const end=source.indexOf('\n  };',start);
assert.ok(start>=0 && end>start,'fee closure must be located exactly');
const closure=source.slice(start,end+5).trim();
const fees=vm.runInNewContext(closure.replace(/^const fees=/,'(').replace(/;$/,'')+')');
let passed=0;
function check(name,fn){fn();passed++;console.log('PASS '+name);}
function near(actual,expected){assert.ok(Math.abs(actual-expected)<1e-8,`expected ${expected}, got ${actual}`);}
check('documented 100k/101k arithmetic vector (NOT capital-feasible)',()=>{
 const r=fees(100000,101000,1);near(r.total,82.718606);assert.equal(r.stt,25);assert.equal(r.brokerage,40);
});
check('capital-bounded 1000/1010 single-share round trip',()=>{
 const r=fees(1000,1010,1);
 const broker=0.3+0.303,exchange=2010*0.0000307,sebi=2010*0.000001;
 const gst=0.18*(broker+exchange+sebi),stamp=1000*0.00003;
 near(r.total,broker+exchange+sebi+gst+stamp);assert.equal(r.stt,0);
});
check('STT rounds down below 0.5 INR',()=>assert.equal(fees(1000,1999,1).stt,0));
check('STT rounds up at 0.5 INR',()=>assert.equal(fees(1000,2000,1).stt,1));
check('brokerage caps at INR 20 per leg',()=>assert.equal(fees(100000,100000,1).brokerage,40));
check('zero quantity has zero charges',()=>near(fees(1000,1010,0).total,0));
console.log(`${passed}/6 synthetic fee tests passed; illustrative current schedule only; 2021 and contract-note reconciliation BLOCKED`);
