#!/usr/bin/env node
/** Offline-only paper replay. No credentials, network access or order routing. */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import {replayBook} from "./guarded_paper_replay.mjs";

const root=process.argv[2],slip=process.argv[3]===undefined?5:Number(process.argv[3]);
if(!root||!Number.isFinite(slip)||slip<0||slip>200)
  throw Error("Usage: node guarded_paper_replay_cli.mjs SOURCE_ROOT [0..200_SLIPPAGE_BPS_PER_SIDE]");
const days=["01","02","03","04","05","08","09","10","11","12","15","16"],results=[];
for(const symbol of ["ACC","RELIANCE"]){
  const sourceFiles=days.map(day=>{
    const filename=path.join(root,"2021","FEB",day+"FEB",day+"FEB",symbol+".txt");
    const content=fs.readFileSync(filename,"utf8");
    return {day,content,sha256:crypto.createHash("sha256").update(content).digest("hex")};
  });
  for(const variant of ["BASELINE","DTT_VETO"]){
    const book=replayBook({symbol,sourceFiles,slippageBps:slip,variant});
    results.push({
      symbol,variant,slippageBps:slip,certified:book.certified,
      knownRealizedPnl:book.knownRealizedPnl,finalEquity:book.finalEquity,
      closedTrades:book.closedTrades,unresolvedPositions:book.unresolvedPositions,
      maxKnownDrawdown:book.maxKnownDrawdown,lockedReason:book.lockedReason,
      stateSummary:book.ledger.reduce((acc,x)=>{
        acc[x.status]=(acc[x.status]||0)+1;return acc;
      },{}),
      ledger:book.ledger,
      sourceFileSha256:sourceFiles.map(x=>({day:x.day,sha256:x.sha256}))
    });
  }
}
console.log(JSON.stringify({
  mode:"OFFLINE_RESEARCH_ONLY",
  priceSource:"third-party unverified February 2021 NSE stock bars",
  charges:"2026 Zerodha-like hypothetical rate scenario, not 2021 contract-note fidelity",
  canTradeLive:false,slippageBpsPerSide:slip,results
},null,2));
