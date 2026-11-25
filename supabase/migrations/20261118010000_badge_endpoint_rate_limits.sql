create table if not exists novex_private.badge_api_rate_limits (
  key_hash text not null check (key_hash ~ '^[0-9a-f]{64}$'),
  action text not null check (action in ('lookup', 'verify')),
  window_bucket bigint not null,
  request_count integer not null default 0 check (request_count >= 0),
  updated_at timestamptz not null default now(),
  primary key (key_hash, action, window_bucket)
);

alter table novex_private.badge_api_rate_limits enable row level security;
revoke all on novex_private.badge_api_rate_limits from public, anon, authenticated;
grant select, insert, update, delete on novex_private.badge_api_rate_limits to service_role;

create or replace function public.novex_consume_badge_rate_limit(
  p_key_hash text,
  p_action text,
  p_limit integer,
  p_window_seconds integer
)
returns boolean
language plpgsql
security definer
set search_path = pg_catalog
as $$
declare
  v_bucket bigint;
  v_count integer;
begin
  if p_key_hash is null or p_key_hash !~ '^[0-9a-f]{64}$'
     or p_action not in ('lookup', 'verify')
     or p_limit < 1 or p_limit > 1000
     or p_window_seconds < 1 or p_window_seconds > 86400 then
    raise exception 'invalid_rate_limit_arguments';
  end if;

  v_bucket := floor(extract(epoch from pg_catalog.now()) / p_window_seconds)::bigint;

  insert into novex_private.badge_api_rate_limits
    (key_hash, action, window_bucket, request_count, updated_at)
  values (p_key_hash, p_action, v_bucket, 1, pg_catalog.now())
  on conflict (key_hash, action, window_bucket) do update
    set request_count = novex_private.badge_api_rate_limits.request_count + 1,
        updated_at = pg_catalog.now()
  returning request_count into v_count;

  -- Opportunistic bounded cleanup; old buckets cannot affect current decisions.
  delete from novex_private.badge_api_rate_limits
  where updated_at < pg_catalog.now() - interval '2 days';

  return v_count <= p_limit;
end;
$$;

revoke all on function public.novex_consume_badge_rate_limit(text, text, integer, integer)
  from public, anon, authenticated;
grant execute on function public.novex_consume_badge_rate_limit(text, text, integer, integer)
  to service_role;
