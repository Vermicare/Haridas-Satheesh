#!/usr/bin/env node
/**
 * Deterministic regression snapshot for the earlier development sample.
 * Does NOT establish accuracy, market-data legality, or profitability.
 */
import fs from "node:fs";
import assert from "node:assert/strict";

if(process.argv.length!==4)throw Error("Usage: node assert_historical_snapshot.mjs RUN_5.json RUN_15.json");
const low=JSON.parse(fs.readFileSync(process.argv[2],"utf8"));
const high=JSON.parse(fs.readFileSync(process.argv[3],"utf8"));
const expected={
  ACC:{
    "5":{BASELINE:{count:9,net:-3.613323},DTT_VETO:{count:4,net:-22.784561}},
    "15":{BASELINE:{count:9,net:-22.987469},DTT_VETO:{count:4,net:-31.688167}}
  },
  RELIANCE:{
    "5":{BASELINE:{count:5,net:17.168397},DTT_VETO:{count:3,net:-34.80653}},
    "15":{BASELINE:{count:5,net:-27.294151},DTT_VETO:{count:3,net:-60.705623}}
  }
};
for(const [slippage,run] of [["5",low],["15",high]]){
  assert.equal(run.slipBpsPerSide,Number(slippage));
  assert.equal(run.output.length,2);
  for(const stock of run.output){
    assert.ok(stock.symbol in expected, "Unknown stock "+stock.symbol);
    assert.equal(stock.validSessions,12,stock.symbol+" missing/invalid sessions");
    assert.equal(stock.excluded.length,0);
    assert.equal(stock.inputFiles.length,12);
    for(const [strategy,goal] of Object.entries(expected[stock.symbol][slippage])){
      const outcome=stock.scenarios[strategy];
      assert.equal(outcome.count,goal.count);
      assert.ok(Math.abs(outcome.netPnl-goal.net)<0.000001,
        stock.symbol+" "+strategy+" "+slippage+" net mismatch: "+outcome.netPnl+" versus "+goal.net);
      assert.ok(Math.abs((outcome.finalEquity-10000)-outcome.netPnl)<0.0000011);
    }
  }
}
console.log("Pinned development-sample reproduction PASS: 24 stock-sessions; 8 net-PnL snapshots matched.");
console.log("This confirms deterministic replay only. No profitable edge, broker fills, or live execution proven.");
