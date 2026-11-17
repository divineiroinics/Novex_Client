# NOVEX identity and in-game badges

## Backend

The NOVEX Supabase project contains private tables under `novex_private`:

- `accounts`, `minecraft_identities`, and `entitlements`: initial NOVEX-account data model.
- `verified_minecraft_profiles`: Minecraft UUID and current username confirmed by Minecraft Services.
- `minecraft_entitlements`: server-managed Standard/Plus tier for a verified Minecraft UUID.

All tables have RLS enabled and no direct grants for browser roles. The registration and lookup RPCs are executable only by `service_role`. The Edge Function keeps the service key server-side.

## How verification works

1. The user completes NOVEX's existing Microsoft → Xbox Live → XSTS → Minecraft sign-in.
2. OneClient sends the resulting short-lived Minecraft Services access token to the NOVEX Edge Function over HTTPS.
3. The Edge Function uses that token once against `https://api.minecraftservices.com/minecraft/profile`.
4. Minecraft Services returns the authoritative UUID and current username. NOVEX stores those two public profile fields and the verification timestamp only.
5. The access token is not stored in Supabase and is not written to application logs.

The token is sent to NOVEX's backend for this check, so this behavior should be disclosed in NOVEX's privacy notice. A successful response means Minecraft Services accepted the token and returned that profile; it does not mean Microsoft has endorsed NOVEX.

## Badge lookup endpoint

`POST /functions/v1/novex-badge-lookup`

Lookup request:
```json
{ "minecraft_uuid": "00000000-0000-4000-8000-000000000000" }
```

Verification request (sent automatically after a successful Microsoft Minecraft login):
```json
{ "action": "verify", "minecraft_access_token": "<short-lived Minecraft Services token>" }
```

The verification response returns the UUID and username confirmed by Minecraft Services. The lookup response returns only whether the UUID is registered and its public Standard/Plus tier. Unregistered identities return `{ "registered": false }`.

## Trust model

- Minecraft Services, not the client-supplied username, is the source of identity proof.
- Offline/cracked UUIDs are not globally verifiable and are excluded from verified badge lookup.
- The Edge Function does not expose service-role credentials.
- Plus entitlement rows must be created by a trusted server-side/admin process; never accept a tier from client metadata.
- The Edge Function currently has no dedicated per-IP/per-UUID rate limiter; add one before public launch.

## Current implementation boundaries

The Fabric mod currently targets Minecraft 1.21.1 only. It adds badge markers to entity display names and player-list entries, subject to runtime mixin verification. The launcher does not yet install it automatically. A trusted Plus purchase/admin workflow, additional Minecraft-version builds, exact NOVEX logo glyph rendering, rate limiting/abuse monitoring, privacy notice updates, and end-to-end multiplayer tests remain open.

Do not present the feature as generally available until launcher installation and all supported-version tests pass.
