# NOVEX identity and in-game badges

## Backend

The NOVEX Supabase project contains private tables under `novex_private`:

- `accounts`: NOVEX account ownership.
- `minecraft_identities`: linked Minecraft UUID, username, account mode and verification state.
- `entitlements`: Standard/Plus membership with source, status and optional expiry.

The tables have RLS enabled and no direct grants for browser roles. The public RPC `novex_lookup_badge` is SECURITY DEFINER with a fixed `search_path`, but EXECUTE is granted only to `service_role`. The Edge Function is the only public lookup surface and keeps the service key server-side.

## Badge lookup endpoint

`POST /functions/v1/novex-badge-lookup`

Request:
```json
{ "minecraft_uuid": "00000000-0000-4000-8000-000000000000" }
```

Responses return only whether the UUID is registered and its public Standard/Plus tier. Unregistered identities return `{ "registered": false }`. The endpoint validates UUID syntax and caches public lookup responses for 30 seconds.

## Trust model

- Only verified online-mode Minecraft identities are returned.
- Usernames are never used as proof of identity.
- Offline/cracked UUIDs are not globally verifiable and are excluded from verified badge lookup. A username or offline UUID can be impersonated.
- The Edge Function does not expose service-role credentials.
- Plus entitlement rows must be created by a trusted server-side/admin process; never accept a tier from client metadata.

## Current implementation boundaries

The Fabric mod currently targets Minecraft 1.21.1 only. It adds badge markers to entity display names and player-list entries, subject to runtime mixin verification. The launcher does not yet install it automatically. Microsoft account linking, a trusted Plus purchase/admin workflow, additional Minecraft-version builds, exact NOVEX logo glyph rendering, rate limiting/abuse monitoring, and end-to-end multiplayer tests remain open.

Do not present the feature as generally available until launcher installation and all supported-version tests pass.
