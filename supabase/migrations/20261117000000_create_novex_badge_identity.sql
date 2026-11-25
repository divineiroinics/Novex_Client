create schema if not exists novex_private;
revoke all on schema novex_private from public, anon, authenticated;
grant usage on schema novex_private to service_role;

create table if not exists novex_private.accounts (
  user_id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists novex_private.minecraft_identities (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  minecraft_uuid uuid not null unique,
  minecraft_username text not null check (char_length(minecraft_username) between 1 and 16),
  account_mode text not null check (account_mode in ('online','offline')),
  verification_status text not null default 'pending'
    check (verification_status in ('pending','verified','rejected')),
  verification_method text check (verification_method in ('microsoft_oauth','in_game_challenge','admin_review')),
  verification_reference text,
  verified_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint verified_identity_has_method check (
    verification_status <> 'verified' or
    (verification_method is not null and verified_at is not null)
  )
);
create index if not exists minecraft_identities_user_id_idx
  on novex_private.minecraft_identities(user_id);

create table if not exists novex_private.entitlements (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  tier text not null check (tier in ('standard','plus')),
  status text not null default 'active' check (status in ('active','expired','revoked')),
  source text not null check (source in ('admin_grant','payment_provider','promotion')),
  external_reference text,
  starts_at timestamptz not null default now(),
  ends_at timestamptz,
  created_at timestamptz not null default now(),
  check (ends_at is null or ends_at > starts_at)
);
create index if not exists entitlements_user_active_idx
  on novex_private.entitlements(user_id, status, starts_at desc);

alter table novex_private.accounts enable row level security;
alter table novex_private.minecraft_identities enable row level security;
alter table novex_private.entitlements enable row level security;
revoke all on all tables in schema novex_private from public, anon, authenticated;
grant select, insert, update, delete on all tables in schema novex_private to service_role;
alter default privileges in schema novex_private
  revoke all on tables from public, anon, authenticated;
alter default privileges in schema novex_private
  grant select, insert, update, delete on tables to service_role;

create or replace function public.novex_lookup_badge(p_minecraft_uuid uuid)
returns table (minecraft_uuid uuid, minecraft_username text, tier text)
language sql stable security definer set search_path = pg_catalog
as $$
  select i.minecraft_uuid, i.minecraft_username,
    case when exists (
      select 1 from novex_private.entitlements e
      where e.user_id = i.user_id and e.tier = 'plus' and e.status = 'active'
        and e.starts_at <= pg_catalog.now()
        and (e.ends_at is null or e.ends_at > pg_catalog.now())
    ) then 'plus' else 'standard' end as tier
  from novex_private.minecraft_identities i
  where i.minecraft_uuid = p_minecraft_uuid
    and i.account_mode = 'online'
    and i.verification_status = 'verified'
  limit 1;
$$;
revoke all on function public.novex_lookup_badge(uuid) from public, anon, authenticated;
grant execute on function public.novex_lookup_badge(uuid) to service_role;
