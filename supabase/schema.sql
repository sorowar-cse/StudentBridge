-- StudentBridge v4. Run once in a NEW Supabase project's SQL Editor as postgres.
-- No API keys or personal information belong in this public file.
begin;
create schema if not exists extensions;
create extension if not exists pgcrypto with schema extensions;
create schema if not exists sb_private;
revoke all on schema sb_private from public, anon, authenticated;

create table if not exists sb_private.settings (
  singleton boolean primary key default true check(singleton),
  quote_key bytea, -- HMAC subkey, installed by runtime/setup_private.sql
  audit_key bytea,
  member_limit integer not null default 15 check(member_limit between 1 and 100000),
  ai_user_daily integer not null default 20,
  ai_global_daily integer not null default 100,
  ai_global_minute integer not null default 3
);
insert into sb_private.settings(singleton) values(true) on conflict do nothing;

create table if not exists public.sb_members (
  user_id uuid primary key references auth.users(id) on delete cascade,
  role text not null default 'executor' check(role in ('viewer','planner','executor')),
  created_at timestamptz not null default now(),
  audit_seq bigint not null default 0,
  audit_head text not null default repeat('0',64)
);
create table if not exists public.sb_documents (
  user_id uuid not null references public.sb_members(user_id) on delete cascade,
  kind text not null check(kind in ('student','plan')),
  encrypted text not null check(length(encrypted) between 56 and 200000),
  updated_at timestamptz not null default now(),
  primary key(user_id,kind)
);
create table if not exists public.sb_wallets (
  user_id uuid not null references public.sb_members(user_id) on delete cascade,
  currency text not null check(currency ~ '^[A-Z]{3}$'),
  balance bigint not null check(balance between 0 and 9000000000000000000),
  primary key(user_id,currency)
);
create table if not exists public.sb_quotes (
  id text primary key check(id ~ '^[0-9a-f]{32}$'),
  user_id uuid not null references public.sb_members(user_id) on delete cascade,
  payload text not null,
  signature text not null,
  expires double precision not null
);
create index if not exists sb_quotes_owner on public.sb_quotes(user_id);
create table if not exists public.sb_transfers (
  quote_id text primary key references public.sb_quotes(id),
  user_id uuid not null references public.sb_members(user_id) on delete cascade,
  receipt jsonb not null,
  executed double precision not null,
  usd numeric not null check(usd > 0)
);
create index if not exists sb_transfers_owner_time on public.sb_transfers(user_id,executed);
create table if not exists public.sb_events (
  user_id uuid not null references public.sb_members(user_id) on delete cascade,
  seq bigint not null, event text not null, stamp double precision not null,
  details jsonb not null, previous text not null, digest text not null,
  primary key(user_id,seq)
);
create table if not exists sb_private.ai_requests (
  user_id uuid not null references public.sb_members(user_id) on delete cascade,
  stamp timestamptz not null default now()
);
create index if not exists sb_ai_time on sb_private.ai_requests(stamp);

-- Tables have read-only, own-row access. All writes use bounded RPCs below.
do $$
declare t text;
begin
  foreach t in array array['sb_members','sb_documents','sb_wallets','sb_quotes','sb_transfers','sb_events'] loop
    execute format('alter table public.%I enable row level security',t);
    execute format('revoke all on public.%I from public, anon, authenticated',t);
    execute format('grant select on public.%I to authenticated',t);
    execute format('drop policy if exists own_rows on public.%I',t);
    execute format('create policy own_rows on public.%I for select to authenticated using ((select auth.uid()) = user_id)',t);
  end loop;
end $$;
revoke all on all tables in schema sb_private from public, anon, authenticated;

create or replace function sb_private.require_member() returns uuid
language plpgsql security definer set search_path='' as $$
declare u uuid := auth.uid();
begin
  if u is null or not exists(select 1 from public.sb_members where user_id=u) then
    raise exception 'SB:Please sign in with an enrolled pilot account.';
  end if;
  return u;
end $$;

create or replace function sb_private.append_event(u uuid, e text, d jsonb) returns void
language plpgsql security definer set search_path='' as $$
declare n bigint; prev text; stamp double precision; dig text; k bytea;
begin
  select audit_seq+1,audit_head into n,prev from public.sb_members where user_id=u for update;
  select audit_key into k from sb_private.settings where singleton;
  if k is null then raise exception 'SB:Private SQL key setup is incomplete.'; end if;
  stamp := extract(epoch from clock_timestamp());
  dig := encode(extensions.hmac(convert_to(jsonb_build_array(u,n,e,stamp,d,prev)::text,'UTF8'),k,'sha256'),'hex');
  insert into public.sb_events values(u,n,e,stamp,d,prev,dig);
  update public.sb_members set audit_seq=n,audit_head=dig where user_id=u;
end $$;

create or replace function sb_private.audit_valid(u uuid) returns boolean
language plpgsql security definer set search_path='' as $$
declare r record; prev text := repeat('0',64); n bigint := 0; expected text; k bytea; head record;
begin
  select audit_key into k from sb_private.settings where singleton;
  if k is null then return false; end if;
  for r in select * from public.sb_events where user_id=u order by seq loop
    n := n+1;
    expected := encode(extensions.hmac(convert_to(jsonb_build_array(u,r.seq,r.event,r.stamp,r.details,r.previous)::text,'UTF8'),k,'sha256'),'hex');
    if r.seq<>n or r.previous<>prev or r.digest<>expected then return false; end if;
    prev := r.digest;
  end loop;
  select audit_seq,audit_head into head from public.sb_members where user_id=u;
  return head.audit_seq=n and head.audit_head=prev;
end $$;

create or replace function public.sb_enroll() returns jsonb
language plpgsql security definer set search_path='' as $$
declare u uuid := auth.uid(); cap integer;
begin
  if u is null or not exists(select 1 from auth.users where id=u and email_confirmed_at is not null) then
    raise exception 'SB:A confirmed pilot account is required.';
  end if;
  -- Serialize enrollment, including simultaneous first logins.
  select member_limit into cap from sb_private.settings where singleton for update;
  if not exists(select 1 from public.sb_members where user_id=u) then
    if (select count(*) from public.sb_members)>=cap then raise exception 'SB:Pilot account limit reached.'; end if;
    insert into public.sb_members(user_id) values(u);
    perform sb_private.append_event(u,'account_enrolled','{}'::jsonb);
  end if;
  return jsonb_build_object('enrolled',true);
end $$;

create or replace function public.sb_save_document(p_kind text,p_encrypted text) returns jsonb
language plpgsql security definer set search_path='' as $$
declare u uuid := sb_private.require_member();
begin
  if p_kind is null or p_kind not in ('student','plan') or p_encrypted is null
    or length(p_encrypted) not between 56 and 200000 or p_encrypted !~ '^[0-9a-f]+$' then
    raise exception 'SB:Invalid encrypted document.';
  end if;
  perform 1 from public.sb_members where user_id=u for update;
  if not sb_private.audit_valid(u) then raise exception 'SB:Audit integrity failed.'; end if;
  insert into public.sb_documents values(u,p_kind,p_encrypted,now())
    on conflict(user_id,kind) do update set encrypted=excluded.encrypted,updated_at=excluded.updated_at;
  perform sb_private.append_event(u,'profile_saved',jsonb_build_object('kind',p_kind));
  return jsonb_build_object('saved',true);
end $$;

create or replace function public.sb_recent_count() returns integer
language sql security definer set search_path='' as $$
  select count(*)::integer from public.sb_transfers
  where user_id=sb_private.require_member() and executed>extract(epoch from now())-1800;
$$;

create or replace function public.sb_top_up(p_currency text,p_minor bigint) returns jsonb
language plpgsql security definer set search_path='' as $$
declare u uuid := sb_private.require_member();
begin
  perform 1 from public.sb_members where user_id=u and role='executor' for update;
  if not found then raise exception 'SB:Only an executor account can top up a sandbox wallet.'; end if;
  if not sb_private.audit_valid(u) then raise exception 'SB:Audit integrity failed.'; end if;
  if p_currency is null or p_currency !~ '^[A-Z]{3}$' or p_minor is null or p_minor<=0 or p_minor>100000000000 then
    raise exception 'SB:Invalid sandbox top-up or amount too large.';
  end if;
  insert into public.sb_wallets values(u,p_currency,p_minor)
    on conflict(user_id,currency) do update set balance=sb_wallets.balance+excluded.balance;
  perform sb_private.append_event(u,'sandbox_top_up',jsonb_build_object('currency',p_currency,'minor',p_minor));
  return jsonb_build_object('saved',true);
end $$;

create or replace function public.sb_create_quote(p_payload text,p_signature text) returns jsonb
language plpgsql security definer set search_path='' as $$
declare u uuid := sb_private.require_member(); q jsonb; k bytea; expected text; ts double precision := extract(epoch from now());
begin
  if length(p_payload)>20000 or p_payload is null then raise exception 'SB:Invalid quote.'; end if;
  select quote_key into k from sb_private.settings where singleton;
  expected := encode(extensions.hmac(convert_to(p_payload,'UTF8'),k,'sha256'),'hex');
  if expected is null or p_signature is null or expected<>p_signature then raise exception 'SB:Quote signature mismatch.'; end if;
  q:=p_payload::jsonb;
  perform 1 from public.sb_members where user_id=u and role in ('planner','executor') for update;
  if not found then raise exception 'SB:Viewer accounts cannot create executable quotes.'; end if;
  if not sb_private.audit_valid(u) then raise exception 'SB:Audit integrity failed.'; end if;
  if (q->>'user_id') is distinct from u::text or (q->>'scope') is distinct from 'sandbox_transfer_v1'
    or (q->>'id') !~ '^[0-9a-f]{32}$' or (q->>'expires')::float8<=ts
    or (q->>'expires')::float8>ts+240 or (q->>'created')::float8>ts+30
    or (q->>'source')=(q->>'target') or (q->>'spend_minor')::bigint<=0
    or (q->>'receive_minor')::bigint<=0 or (q->>'usd')::numeric<=0
    or (q->>'source_digits')::int not between 0 and 4 or (q->>'target_digits')::int not between 0 and 4 then
    raise exception 'SB:Quote capability mismatch or expired quote.';
  end if;
  insert into public.sb_quotes values(q->>'id',u,p_payload,p_signature,(q->>'expires')::float8);
  perform sb_private.append_event(u,'quote_created',jsonb_build_object('id',q->>'id','risk',q->'risk','mode',q->'reference'->>'mode'));
  return jsonb_build_object('saved',true);
end $$;

create or replace function public.sb_execute(p_quote_id text,p_confirmation text,p_approved boolean) returns jsonb
language plpgsql security definer set search_path='' as $$
declare u uuid := sb_private.require_member(); r record; q jsonb; receipt jsonb;
  ts double precision := extract(epoch from now()); spent bigint; received bigint; available bigint; used numeric; k bytea;
begin
  -- One account row is the mutex for wallet updates, replay, limits and audit.
  perform 1 from public.sb_members where user_id=u and role='executor' for update;
  if not found then raise exception 'SB:This account cannot execute sandbox transfers.'; end if;
  if not sb_private.audit_valid(u) then raise exception 'SB:Audit integrity failed.'; end if;
  select * into r from public.sb_quotes where id=p_quote_id and user_id=u;
  if not found then raise exception 'SB:Quote does not belong to this account.'; end if;
  select quote_key into k from sb_private.settings where singleton;
  if r.signature<>encode(extensions.hmac(convert_to(r.payload,'UTF8'),k,'sha256'),'hex') then
    raise exception 'SB:Quote signature mismatch.';
  end if;
  select t.receipt into receipt from public.sb_transfers t where t.quote_id=p_quote_id and t.user_id=u;
  if found then return receipt || jsonb_build_object('replayed',true); end if;
  q:=r.payload::jsonb;
  if r.expires<=ts then raise exception 'SB:Quote expired. Generate a fresh quote.'; end if;
  if p_approved is distinct from true or p_confirmation is distinct from right(p_quote_id,6) then
    raise exception 'SB:Review the quote, tick approval and enter its final six characters.';
  end if;
  if (q->>'usd')::numeric>2000 then raise exception 'SB:Per-transfer sandbox limit is USD 2,000 equivalent.'; end if;
  if (q->'risk'->>'blocked')::boolean is distinct from false then raise exception 'SB:Risk gate requires review.'; end if;
  if (select count(*) from public.sb_transfers where user_id=u and executed>ts-1800)>=5 then
    raise exception 'SB:Transfer frequency limit reached.';
  end if;
  select coalesce(sum(usd),0) into used from public.sb_transfers where user_id=u and executed>=floor(ts/86400)*86400;
  if used+(q->>'usd')::numeric>5000 then raise exception 'SB:Daily sandbox limit is USD 5,000 equivalent.'; end if;
  spent:=(q->>'spend_minor')::bigint; received:=(q->>'receive_minor')::bigint;
  select balance into available from public.sb_wallets where user_id=u and currency=q->>'source';
  if coalesce(available,0)<spent then raise exception 'SB:Insufficient sandbox balance.'; end if;
  update public.sb_wallets set balance=balance-spent where user_id=u and currency=q->>'source';
  insert into public.sb_wallets values(u,q->>'target',received)
    on conflict(user_id,currency) do update set balance=sb_wallets.balance+excluded.balance;
  receipt:=jsonb_build_object('quote_id',p_quote_id,'source',q->>'source','target',q->>'target',
    'spent',round(spent/power(10::numeric,(q->>'source_digits')::int),(q->>'source_digits')::int)::text,
    'fee_included',round((q->>'fee_minor')::numeric/power(10::numeric,(q->>'source_digits')::int),(q->>'source_digits')::int)::text,
    'received',round(received/power(10::numeric,(q->>'target_digits')::int),(q->>'target_digits')::int)::text,
    'provider',q->>'provider','fx_mode',q->'reference'->>'mode','executed_at',ts,
    'usd_equivalent',q->>'usd','status','Sandbox completed — no real money moved','replayed',false);
  insert into public.sb_transfers values(p_quote_id,u,receipt,ts,(q->>'usd')::numeric);
  perform sb_private.append_event(u,'sandbox_transfer_completed',receipt);
  return receipt;
end $$;

create or replace function public.sb_reserve_ai() returns jsonb
language plpgsql security definer set search_path='' as $$
declare u uuid := sb_private.require_member(); s record;
begin
  select * into s from sb_private.settings where singleton for update;
  if (select count(*) from sb_private.ai_requests where stamp>=date_trunc('day',now() at time zone 'UTC') at time zone 'UTC' and user_id=u)>=s.ai_user_daily
    or (select count(*) from sb_private.ai_requests where stamp>=date_trunc('day',now() at time zone 'UTC') at time zone 'UTC')>=s.ai_global_daily
    or (select count(*) from sb_private.ai_requests where stamp>now()-interval '1 minute')>=s.ai_global_minute then
    raise exception 'SB:StudentBridge AI allowance reached. Wait or use the built-in calculations.';
  end if;
  -- Count attempts, including provider failures. Never store the student's question.
  insert into sb_private.ai_requests(user_id) values(u);
  delete from sb_private.ai_requests where stamp<now()-interval '8 days';
  return jsonb_build_object('reserved',true);
end $$;

create or replace function public.sb_export_audit() returns jsonb
language plpgsql security definer set search_path='' as $$
declare u uuid := sb_private.require_member(); m record; events jsonb; valid boolean;
begin
  perform 1 from public.sb_members where user_id=u for update;
  valid:=sb_private.audit_valid(u);
  select audit_seq,audit_head into m from public.sb_members where user_id=u;
  select coalesce(jsonb_agg(jsonb_build_object('seq',seq,'event',event,'stamp',stamp,'digest',digest,'details',details) order by seq),'[]'::jsonb)
    into events from public.sb_events where user_id=u;
  return jsonb_build_object('global_integrity',jsonb_build_object('valid',valid,'rows',m.audit_seq,'head',m.audit_head,
    'reason','Verified per-user database HMAC chain; database owner remains trusted'),
    'own_events',events,'note','Own-account export only. Save the head externally to compare later checkpoints.');
end $$;

create or replace function public.sb_clear_personal_data() returns jsonb
language plpgsql security definer set search_path='' as $$
declare u uuid := sb_private.require_member();
begin
  perform 1 from public.sb_members where user_id=u for update;
  if not sb_private.audit_valid(u) then raise exception 'SB:Audit integrity failed.'; end if;
  delete from public.sb_documents where user_id=u;
  perform sb_private.append_event(u,'personal_profiles_deleted','{}'::jsonb);
  return jsonb_build_object('deleted',true);
end $$;

-- No PUBLIC execute grants, including the private helper functions.
revoke all on all functions in schema sb_private from public, anon, authenticated;
do $$
declare r record;
begin
  for r in select p.oid::regprocedure as signature from pg_proc p join pg_namespace n on n.oid=p.pronamespace
    where n.nspname='public' and p.proname like 'sb_%' loop
    execute format('revoke all on function %s from public, anon, authenticated',r.signature);
    execute format('grant execute on function %s to authenticated',r.signature);
  end loop;
end $$;
commit;
