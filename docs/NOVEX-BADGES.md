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
- The Edge Function applies atomic per-client-address limits: 120 badge lookups per minute and 5 verification attempts per hour. It stores only a keyed HMAC-SHA-256 address hash, not the raw address, and fails closed if the limiter database call is unavailable. These limits are a baseline abuse control, not a substitute for monitoring or provider-level DDoS protection.

## Current implementation boundaries

The Fabric mod currently targets Minecraft 1.21.1 only. The Windows nightly build compiles it into the launcher, which installs it into Fabric 1.21.1 instances at launch without replacing an existing file. Badge lookups are inert unless the launcher has written a local consent marker after the user accepts the updated privacy notice; declining removes that marker. The mod adds badge markers to entity display names and player-list entries, but live in-game mixin behavior still requires multiplayer testing. A trusted Plus purchase/admin workflow, additional Minecraft-version builds, and end-to-end multiplayer tests remain open. The Edge Function applies server-side per-address rate limits; production monitoring and abuse response still need configuration.

Do not present the feature as generally available until launcher installation and all supported-version tests pass.
