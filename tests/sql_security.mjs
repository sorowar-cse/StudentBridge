/** Real PostgreSQL execution in WASM, including pgcrypto and RLS.
 * Auth's signed-token verification is Supabase's responsibility; auth.uid() is
 * stubbed here to exercise the database boundary without a cloud account.
 * This is not a live Supabase, HTTP, or multi-process load test.
 */
import {PGlite} from '@electric-sql/pglite';
import {pgcrypto} from '@electric-sql/pglite/contrib/pgcrypto';
import {createHmac, randomBytes} from 'node:crypto';
import {readFileSync, writeFileSync, mkdirSync} from 'node:fs';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';

const root=fileURLToPath(new URL('../',import.meta.url));
const db=new PGlite({extensions:{pgcrypto}});
const checks=[];
const master=Buffer.alloc(32,0x12); // Synthetic test key, never used by a deployment.
const subkey=name=>createHmac('sha256',master).update(name).digest();
const signing=subkey('quote-signing-v1');
const ids=Array.from({length:17},(_,i)=>`00000000-0000-4000-8000-${String(i+1).padStart(12,'0')}`);
const canonical=x=>Array.isArray(x)?`[${x.map(canonical).join(',')}]`:
  x&&typeof x==='object'?`{${Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+canonical(x[k])).join(',')}}`:JSON.stringify(x);
async function check(name,fn){await fn();checks.push({name,passed:true});console.log('PASS',name);}
async function asUser(id,fn,role='authenticated'){
  return db.transaction(async tx=>{
    await tx.exec(`set local role ${role}`);
    await tx.query("select set_config('request.jwt.claim.sub',$1,true)",[id||'']);
    return fn(tx);
  });
}
async function rpc(id,name,args=[]){
  assert.match(name,/^sb_[a-z_]+$/);
  const r=await asUser(id,tx=>tx.query(`select public.${name}(${args.map((_,i)=>'$'+(i+1)).join(',')}) as result`,args));
  return r.rows[0].result;
}
async function denied(fn,pattern){await assert.rejects(fn,pattern);}
function quote(id,overrides={}){
  const now=Date.now()/1000;
  return {id:randomBytes(16).toString('hex'),user_id:id,scope:'sandbox_transfer_v1',created:now,expires:now+180,
    source:'USD',target:'CNY',source_digits:2,target_digits:2,spend_minor:10000,fee_minor:50,
    receive_minor:65000,usd:'100',provider:'Campus',risk:{blocked:false},reference:{mode:'demo'},...overrides};
}
async function save(q){const p=canonical(q);await rpc(q.user_id,'sb_create_quote',[p,createHmac('sha256',signing).update(p).digest('hex')]);return q;}
const execute=(id,q,approved=true,confirmation=q.id.slice(-6))=>rpc(id,'sb_execute',[q.id,confirmation,approved]);

try{
  await db.exec(`create role anon; create role authenticated; create schema auth;
    create table auth.users(id uuid primary key,email text,email_confirmed_at timestamptz);
    create function auth.uid() returns uuid language sql stable as $$ select nullif(current_setting('request.jwt.claim.sub',true),'')::uuid $$;
    grant usage on schema auth to anon, authenticated; grant execute on function auth.uid() to anon, authenticated;`);
  await db.exec(readFileSync(root+'supabase/schema.sql','utf8'));
  await db.query("update sb_private.settings set quote_key=decode($1,'hex'),audit_key=decode($2,'hex')",
    [signing.toString('hex'),subkey('audit-v1').toString('hex')]);
  for(let i=0;i<ids.length;i++)await db.query('insert into auth.users values($1,$2,now())',[ids[i],`synthetic-${i}@example.org`]);

  await check('15 accounts enroll; account 16 is rejected',async()=>{
    for(const id of ids.slice(0,15))assert.equal((await rpc(id,'sb_enroll')).enrolled,true);
    await denied(()=>rpc(ids[15],'sb_enroll'),/Pilot account limit/);
  });
  await check('Re-enrollment is idempotent',async()=>{
    await rpc(ids[0],'sb_enroll');assert.equal((await db.query('select count(*)::int n from public.sb_members')).rows[0].n,15);
  });
  await check('Unconfirmed accounts are rejected',async()=>{
    await db.query('update auth.users set email_confirmed_at=null where id=$1',[ids[16]]);
    await denied(()=>rpc(ids[16],'sb_enroll'),/confirmed pilot/);
  });
  await check('Anonymous reads and RPC execution are denied',async()=>{
    await denied(()=>asUser(null,tx=>tx.query('select * from public.sb_documents'),'anon'),/permission denied/);
    await denied(()=>asUser(null,tx=>tx.query('select public.sb_enroll()'),'anon'),/permission denied/);
  });
  await check('Private keys and helper functions cannot be accessed',async()=>{
    await denied(()=>asUser(ids[0],tx=>tx.query('select * from sb_private.settings')),/permission denied/);
    await denied(()=>asUser(ids[0],tx=>tx.query('select sb_private.audit_valid($1)',[ids[0]])),/permission denied/);
  });
  await check('Own profile is readable; another user sees no rows',async()=>{
    await rpc(ids[0],'sb_save_document',['student','a'.repeat(64)]);
    const a=await asUser(ids[0],tx=>tx.query('select * from public.sb_documents'));
    const b=await asUser(ids[1],tx=>tx.query('select * from public.sb_documents'));
    assert.equal(a.rows.length,1);assert.equal(b.rows.length,0);
    const cross=await asUser(ids[1],tx=>tx.query('select * from public.sb_documents where user_id=$1',[ids[0]]));
    assert.equal(cross.rows.length,0);
  });
  await check('Direct table writes and role escalation are denied',async()=>{
    await denied(()=>asUser(ids[1],tx=>tx.query('update public.sb_documents set encrypted=$1 where user_id=$2',['b'.repeat(64),ids[0]])),/permission denied/);
    await denied(()=>asUser(ids[1],tx=>tx.query("update public.sb_members set role='executor'")),/permission denied/);
    await denied(()=>asUser(ids[0],tx=>tx.query("insert into public.sb_wallets values($1,'USD',999999)",[ids[0]])),/permission denied/);
  });
  await check('Quotes need the server signing key',async()=>{
    await denied(()=>rpc(ids[0],'sb_create_quote',[canonical(quote(ids[0])),'0'.repeat(64)]),/signature mismatch/);
    const q=quote(ids[0]);const original=canonical(q);q.spend_minor=1;
    await denied(()=>rpc(ids[0],'sb_create_quote',[canonical(q),createHmac('sha256',signing).update(original).digest('hex')]),/signature mismatch/);
  });
  await rpc(ids[0],'sb_top_up',['USD',10000000]);
  const first=await save(quote(ids[0]));
  await check('Cross-account execution cannot read or spend a quote',async()=>{
    await denied(()=>execute(ids[1],first),/does not belong/);
  });
  await check('Approval and confirmation are both enforced',async()=>{
    await denied(()=>execute(ids[0],first,false),/tick approval/);
    await denied(()=>execute(ids[0],first,true,'BADBAD'),/tick approval/);
    assert.equal((await db.query("select balance from public.sb_wallets where user_id=$1 and currency='USD'",[ids[0]])).rows[0].balance,10000000);
  });
  await check('Retry returns the receipt with a single debit',async()=>{
    const receipts=await Promise.all([execute(ids[0],first),execute(ids[0],first)]);
    assert.equal(receipts.filter(r=>r.replayed).length,1);
    assert.equal((await db.query("select balance from public.sb_wallets where user_id=$1 and currency='USD'",[ids[0]])).rows[0].balance,9990000);
    assert.equal((await db.query('select count(*)::int n from public.sb_transfers where quote_id=$1',[first.id])).rows[0].n,1);
    assert.equal(receipts[0].spent,'100.00');
  });
  await check('Expiry uses database time',async()=>{
    const q=await save(quote(ids[0]));await db.query('update public.sb_quotes set expires=0 where id=$1',[q.id]);
    await denied(()=>execute(ids[0],q),/expired/);
  });
  await check('Risk and per-transfer limit are enforced in SQL',async()=>{
    await denied(async()=>execute(ids[0],await save(quote(ids[0],{risk:{blocked:true}}))),/Risk gate/);
    await denied(async()=>execute(ids[0],await save(quote(ids[0],{usd:'2000.01'}))),/Per-transfer/);
  });
  await check('Daily limit is enforced across different quote IDs',async()=>{
    for(const usd of ['1900','1900','1100'])await execute(ids[0],await save(quote(ids[0],{usd})));
    await denied(async()=>execute(ids[0],await save(quote(ids[0],{usd:'0.01'}))),/Daily sandbox/);
  });
  await check('Frequency limit is enforced at execution',async()=>{
    await rpc(ids[2],'sb_top_up',['USD',10000000]);
    for(let i=0;i<5;i++)await execute(ids[2],await save(quote(ids[2])));
    await denied(async()=>execute(ids[2],await save(quote(ids[2]))),/frequency/);
  });
  await check('Viewer and planner permission tiers are enforced',async()=>{
    await db.query("update public.sb_members set role='viewer' where user_id=$1",[ids[3]]);
    await denied(()=>rpc(ids[3],'sb_top_up',['USD',100]),/executor/);
    await denied(()=>save(quote(ids[3])),/Viewer/);
    await db.query("update public.sb_members set role='planner' where user_id=$1",[ids[4]]);
    const q=await save(quote(ids[4]));await denied(()=>execute(ids[4],q),/cannot execute/);
  });
  await check('Insufficient balance rolls back without receipt',async()=>{
    const q=await save(quote(ids[5]));await denied(()=>execute(ids[5],q),/Insufficient/);
    assert.equal((await db.query('select count(*)::int n from public.sb_transfers where quote_id=$1',[q.id])).rows[0].n,0);
  });
  await check('Global AI allowance is bounded across users',async()=>{
    for(let i=0;i<3;i++)await rpc(ids[i],'sb_reserve_ai');
    await denied(()=>rpc(ids[3],'sb_reserve_ai'),/allowance/);
  });
  await check('Per-user and global daily AI allowances are enforced',async()=>{
    await db.exec('delete from sb_private.ai_requests; update sb_private.settings set ai_user_daily=2,ai_global_daily=100,ai_global_minute=100;');
    await rpc(ids[0],'sb_reserve_ai');await rpc(ids[0],'sb_reserve_ai');
    await denied(()=>rpc(ids[0],'sb_reserve_ai'),/allowance/);
    await db.exec('delete from sb_private.ai_requests; update sb_private.settings set ai_user_daily=20,ai_global_daily=1;');
    await rpc(ids[0],'sb_reserve_ai');
    await denied(()=>rpc(ids[1],'sb_reserve_ai'),/allowance/);
  });
  await check('Audit export is own-account only and detects event changes',async()=>{
    const a=await rpc(ids[0],'sb_export_audit');assert.equal(a.global_integrity.valid,true);
    const b=await rpc(ids[1],'sb_export_audit');assert.equal(b.own_events.some(e=>e.event==='sandbox_transfer_completed'),false);
    const original=(await db.query('select details from public.sb_events where user_id=$1 and seq=1',[ids[0]])).rows[0].details;
    await db.query("update public.sb_events set details='{}'::jsonb || jsonb_build_object('tampered',true) where user_id=$1 and seq=1",[ids[0]]);
    assert.equal((await rpc(ids[0],'sb_export_audit')).global_integrity.valid,false);
    await denied(()=>rpc(ids[0],'sb_top_up',['USD',100]),/Audit integrity/);
    await db.query('update public.sb_events set details=$1 where user_id=$2 and seq=1',[JSON.stringify(original),ids[0]]);
    assert.equal((await rpc(ids[0],'sb_export_audit')).global_integrity.valid,true);
  });
  await check('Deleting another account does not affect the owner document',async()=>{
    await rpc(ids[1],'sb_clear_personal_data');
    assert.equal((await asUser(ids[0],tx=>tx.query('select * from public.sb_documents'))).rows.length,1);
    await rpc(ids[0],'sb_clear_personal_data');
    assert.equal((await asUser(ids[0],tx=>tx.query('select * from public.sb_documents'))).rows.length,0);
  });
  await check('Schema can be reapplied without deleting user data',async()=>{
    await db.exec(readFileSync(root+'supabase/schema.sql','utf8'));
    assert.equal((await rpc(ids[0],'sb_export_audit')).global_integrity.valid,true);
  });
  await check('Owner full account deletion cascades profiles and ledger, releasing an enrollment slot',async()=>{
    await db.query('delete from auth.users where id=$1',[ids[0]]);
    for(const table of ['sb_members','sb_documents','sb_quotes','sb_transfers','sb_wallets','sb_events']){
      assert.equal((await db.query(`select count(*)::int n from public.${table} where user_id=$1`,[ids[0]])).rows[0].n,0);
    }
    assert.equal((await rpc(ids[15],'sb_enroll')).enrolled,true);
  });
  mkdirSync(root+'evaluation',{recursive:true});
  writeFileSync(root+'evaluation/v4_sql_verification.json',JSON.stringify({engine:'PGlite PostgreSQL + pgcrypto',
    scope:'Auth claim stub; real PostgreSQL RLS/RPCs, not hosted Supabase/load testing',checks},null,2));
  console.log(`Completed ${checks.length} SQL security checks.`);
}finally{await db.close();}
