create table if not exists novex_private.verified_minecraft_profiles (
  minecraft_uuid uuid primary key,
  minecraft_username text not null check (char_length(minecraft_username) between 1 and 16),
  verified_at timestamptz not null default now(),
  verification_method text not null default 'minecraft_services_profile'
    check (verification_method = 'minecraft_services_profile'),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists novex_private.minecraft_entitlements (
  minecraft_uuid uuid not null references novex_private.verified_minecraft_profiles(minecraft_uuid) on delete cascade,
  tier text not null check (tier in ('standard','plus')),
  status text not null default 'active' check (status in ('active','expired','revoked')),
  starts_at timestamptz not null default now(),
  ends_at timestamptz,
  updated_at timestamptz not null default now(),
  primary key (minecraft_uuid, tier),
  check (ends_at is null or ends_at > starts_at)
);

alter table novex_private.verified_minecraft_profiles enable row level security;
alter table novex_private.minecraft_entitlements enable row level security;
revoke all on novex_private.verified_minecraft_profiles, novex_private.minecraft_entitlements
  from public, anon, authenticated;
grant select, insert, update, delete on novex_private.verified_minecraft_profiles,
  novex_private.minecraft_entitlements to service_role;

create or replace function public.novex_register_verified_profile(
  p_minecraft_uuid uuid,
  p_minecraft_username text
)
returns void
language plpgsql
security definer
set search_path = pg_catalog
as $$
begin
  if p_minecraft_username is null or char_length(p_minecraft_username) not between 1 and 16 then
    raise exception 'invalid_minecraft_username';
  end if;

  insert into novex_private.verified_minecraft_profiles (
    minecraft_uuid, minecraft_username, verified_at, updated_at
  ) values (
    p_minecraft_uuid, p_minecraft_username, pg_catalog.now(), pg_catalog.now()
  )
  on conflict (minecraft_uuid) do update set
    minecraft_username = excluded.minecraft_username,
    verified_at = pg_catalog.now(),
    updated_at = pg_catalog.now();
end;
$$;
revoke all on function public.novex_register_verified_profile(uuid, text) from public, anon, authenticated;
grant execute on function public.novex_register_verified_profile(uuid, text) to service_role;

create or replace function public.novex_lookup_badge(p_minecraft_uuid uuid)
returns table (minecraft_uuid uuid, minecraft_username text, tier text)
language sql
stable
security definer
set search_path = pg_catalog
as $$
  select p.minecraft_uuid, p.minecraft_username,
    case when exists (
      select 1 from novex_private.minecraft_entitlements e
      where e.minecraft_uuid = p.minecraft_uuid and e.tier = 'plus' and e.status = 'active'
        and e.starts_at <= pg_catalog.now()
        and (e.ends_at is null or e.ends_at > pg_catalog.now())
    ) then 'plus' else 'standard' end as tier
  from novex_private.verified_minecraft_profiles p
  where p.minecraft_uuid = p_minecraft_uuid
  limit 1;
$$;
revoke all on function public.novex_lookup_badge(uuid) from public, anon, authenticated;
grant execute on function public.novex_lookup_badge(uuid) to service_role;
