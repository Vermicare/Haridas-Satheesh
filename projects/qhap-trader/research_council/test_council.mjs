import test from 'node:test';
import assert from 'node:assert/strict';
import {validateBrief,validateModels,panelPrompt,judgePrompt,
  runCouncil,verifyAudit,openRouterComplete,syntheticClient} from './council.mjs';

const brief={
  project:'QHAP-TRADER',title:'Falsify an intraday abstention hypothesis',
  question:'How can a frozen Indian equity hypothesis be falsified against NO_TRADE on licensed unseen data?',
  sources:['https://github.com/Vermicare/Haridas-Satheesh/issues/27'],
  publicOnly:true,realOrderExecution:false,usesPrivateMarketData:false
};
const models=['anthropic/claude-test','openai/gpt-test','google/gemini-test'];
const run=client=>runCouncil({brief,models,judge:'openai/judge-test',
  client:client||syntheticClient()});

test('accept a strictly public, explicitly no-trade research brief',()=>{
  assert.equal(validateBrief(brief).realOrderExecution,false);
});
test('reject any private market-data or real-order authorization',()=>{
  for(const patch of [{usesPrivateMarketData:true},{realOrderExecution:true},
    {publicOnly:false},{project:'OTHER'}])
    assert.throws(()=>validateBrief({...brief,...patch}));
});
test('reject likely credential patterns in questions',()=>{
  for(const question of ['sk-or-v1-012345678901234','Authorization: Bearer abc',
    'api_key=private','password=oops'])
    assert.throws(()=>validateBrief({...brief,question}));
});
test('reject private, credential-bearing or insecure URLs',()=>{
  for(const source of ['http://example.com/a','https://localhost/x',
    'https://127.0.0.1/','https://user:pass@example.com/x',
    'https://example.org/?token=test'])
    assert.throws(()=>validateBrief({...brief,sources:[source]}));
});
test('require three distinct provider families and a real judge ID',()=>{
  assert.deepEqual(validateModels(models,'openai/judge-test').models,models);
  assert.throws(()=>validateModels(['openai/a','openai/b','google/c'],'openai/j'));
  assert.throws(()=>validateModels(['anthropic/a','openai/b'],'openai/j'));
  assert.throws(()=>validateModels(['fake/a','openai/b','google/c'],'openai/j'));
});
test('panel prompt contains task but no other model outputs',()=>{
  const p=panelPrompt(brief,'SKEPTIC');
  assert.match(p,/SKEPTIC/);
  assert.doesNotMatch(p,/UNTRUSTED_PANEL_1/);
});
test('judge receives all three answers labelled untrusted',()=>{
  const p=judgePrompt(brief,models.map(model=>({model,text:'synthetic'})));
  assert.match(p,/UNTRUSTED_PANEL_1/);
  assert.match(p,/UNTRUSTED_PANEL_3/);
  assert.match(p,/RESEARCH_ONLY/);
});
test('three independent calls and one judge, with orders always disabled',async()=>{
  const client=syntheticClient(),r=await run(client);
  assert.deepEqual(client.calls,models.concat('openai/judge-test'));
  assert.equal(r.panel.length,3);
  assert.equal(r.tradeAuthorization,false);
  assert.equal(r.ordersSubmitted,0);
  assert.equal(r.verifiedProfitableEdge,false);
});
test('synthetic demo is deterministic and its audit hash verifies',async()=>{
  const a=await run(),b=await run();
  assert.equal(a.auditSha256,b.auditSha256);
  assert.equal(verifyAudit(a),true);
});
test('tampering with an individual model response fails validation',async()=>{
  const a=await run();
  a.panel[1].text+='inserted fake win';
  assert.equal(verifyAudit(a),false);
});
test('tampering with the judge response fails validation',async()=>{
  const a=await run();
  a.synthesis+='invented';
  assert.equal(verifyAudit(a),false);
});
test('changing trade authorization fails validation',async()=>{
  const a=await run();
  a.tradeAuthorization=true;
  assert.equal(verifyAudit(a),false);
});
test('panel errors prevent judge execution and final report',async()=>{
  let judgeCalls=0;
  const client={async complete({model}){
    if(model.includes('gemini'))throw Error('SYNTHETIC_NETWORK_FAILURE');
    if(model.includes('judge'))judgeCalls++;
    return 'test only';
  }};
  await assert.rejects(()=>run(client),/SYNTHETIC_NETWORK_FAILURE/);
  assert.equal(judgeCalls,0);
});
test('empty model response fails, no judge conclusion',async()=>{
  await assert.rejects(()=>run({async complete({model}){
    return model.includes('gpt')?'':'test response';
  }}),/BAD_AI_RESPONSE/);
});
test('no API key or billable opt-in prevents network access',async()=>{
  const old=process.env.QHAP_ENABLE_PAID_COUNCIL;
  delete process.env.QHAP_ENABLE_PAID_COUNCIL;
  try{
    await assert.rejects(()=>openRouterComplete({model:'openai/test',
      system:'test',user:'test',maxTokens:20},
      async()=>{throw Error('UNEXPECTED_NETWORK')},'unit-test-key'),
      /LOCAL_KEY_AND_EXPLICIT_COST_OPT_IN_REQUIRED/);
  }finally{
    if(old===undefined)delete process.env.QHAP_ENABLE_PAID_COUNCIL;
    else process.env.QHAP_ENABLE_PAID_COUNCIL=old;
  }
});
test('opt-in mock goes only to fixed OpenRouter chat endpoint',async()=>{
  const old=process.env.QHAP_ENABLE_PAID_COUNCIL;
  process.env.QHAP_ENABLE_PAID_COUNCIL='I_ACCEPT_AI_API_COSTS';
  let called=0;
  try{
    const r=await openRouterComplete({model:'openai/test',system:'a',
      user:'b',maxTokens:20},async(url,opt)=>{
      called++;
      assert.equal(url,'https://openrouter.ai/api/v1/chat/completions');
      assert.equal(opt.method,'POST');
      const body=JSON.parse(opt.body);
      assert.equal(body.model,'openai/test');
      assert.equal(body.stream,false);
      return {ok:true,async json(){return {choices:[{message:{content:'UNVERIFIED'}}]}}};
    },'unit-test-key');
    assert.equal(called,1);assert.equal(r,'UNVERIFIED');
  }finally{
    if(old===undefined)delete process.env.QHAP_ENABLE_PAID_COUNCIL;
    else process.env.QHAP_ENABLE_PAID_COUNCIL=old;
  }
});
test('HTTP errors reveal status only, not token or response body',async()=>{
  const old=process.env.QHAP_ENABLE_PAID_COUNCIL;
  process.env.QHAP_ENABLE_PAID_COUNCIL='I_ACCEPT_AI_API_COSTS';
  try{
    await assert.rejects(()=>openRouterComplete({model:'openai/test',
      system:'a',user:'b',maxTokens:20},async()=>({ok:false,status:429}),
      'unit-test-key'),/OPENROUTER_HTTP_429/);
  }finally{
    if(old===undefined)delete process.env.QHAP_ENABLE_PAID_COUNCIL;
    else process.env.QHAP_ENABLE_PAID_COUNCIL=old;
  }
});
test('model hallucination can only become untrusted text, never orders',async()=>{
  const a=await run({async complete(){return 'BUY NOW 100 SHARES'}});
  assert.equal(a.ordersSubmitted,0);
  assert.equal(a.tradeAuthorization,false);
  assert.equal(a.independentMarketTestPassed,false);
});
