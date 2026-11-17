# NOVEX Badges (Fabric)

Client-side badge renderer for verified NOVEX Minecraft identities.

## Current target

- Minecraft Java 1.21.1
- Fabric Loader 0.16+
- Java 21

This first build target is intentionally explicit. It is **not yet compatible with every Minecraft version supported by OneClient**; each additional game version needs its own compile and runtime validation.

## Behavior

- Reads a player's UUID from the normal Minecraft client profile.
- Looks up verified identity and Standard/Plus tier through the NOVEX badge Edge Function.
- Caches results for 90 seconds and performs HTTP requests asynchronously.
- Adds a compact badge marker to player display names and player-list entries.
- Does not trust a username, client-supplied tier, or offline-mode UUID.

The database lookup only returns identities verified by Minecraft Services. When a player completes the launcher's existing Microsoft → Xbox → Minecraft sign-in, NOVEX sends the resulting short-lived Minecraft Services access token to its Edge Function. The function calls Minecraft's official profile endpoint, stores only the returned UUID and current username, and discards the token. The token is not written to logs or the database. Offline/cracked UUIDs cannot be verified this way and are not awarded globally trusted badges.

## Build

Run from this directory with Gradle 8.10.2 and Java 21:

```sh
gradle build
```

The jar is written to `build/libs/`.

## Important integration status

This is still a standalone mod project. The launcher now submits Microsoft-authenticated Minecraft profiles for server-side verification, but it does not yet bundle or auto-install this jar into Fabric instances. Plus entitlement administration, exact NOVEX emblem glyph/texture, additional Minecraft-version builds, rate limiting/abuse monitoring, and end-to-end multiplayer tests remain follow-up work. Do not advertise the badge system as production-ready until those are complete.
