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

The database lookup only returns identities that are both verified and in online account mode. Offline/cracked UUIDs are not globally trustworthy: they can be spoofed by another client, so this service does not award globally visible verified badges to them.

## Build

Run from this directory with Gradle 8.10.2 and Java 21:

```sh
gradle build
```

The jar is written to `build/libs/`.

## Important integration status

This is a standalone mod project. The OneClient launcher does not yet bundle or auto-install this jar into Fabric instances. That launcher integration, Microsoft account linking, plus entitlement administration, exact NOVEX emblem glyph/texture, and testing against other supported Minecraft versions remain follow-up work. Do not advertise the badge system as production-ready until those are complete.
