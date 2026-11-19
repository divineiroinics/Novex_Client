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

The stable badge build discovers every Fabric version in NOVEX's curated catalog and builds a matching jar for Minecraft 1.18 through 1.21.11 and Minecraft 26+. It also retains the previously shipped 1.21.1, 1.21.4, 1.21.5, and 1.21.8 targets even if they are removed from the catalog's quick-pick list. Windows nightlies additionally attempt the newest Fabric snapshot/RC/pre-release for each supported source family (legacy 1.x and modern 26+), plus the latest modern weekly snapshot; a preview is embedded only when Fabric mappings/loader are published and the current code compiles. Preview failures are warnings and do not block stable builds. Signed releases intentionally include stable catalog targets only. The launcher selects and installs an exact-version jar for the active Fabric instance without replacing a user-managed file. Legacy 1.x versions use matching Yarn mappings; 26+ uses a separate Mojang-mapped source set. Older weekly snapshot identifiers are not built; the latest current weekly snapshot is attempted on nightlies only. Versions before 1.18 and non-Fabric loaders are not included. Badge lookups are inert unless the launcher has written a local consent marker after the user accepts the updated privacy notice; declining removes that marker. The mod adds badge markers to the local player's display name and Tab player-list entry, and verified badges to other players, but live in-game behavior still requires multiplayer testing. A trusted Plus purchase/admin workflow and end-to-end multiplayer tests remain open. The Edge Function applies server-side per-address rate limits; production monitoring and abuse response still need configuration.

Do not present the feature as generally available until launcher installation and all supported-version tests pass.
