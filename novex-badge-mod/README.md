# NOVEX Badges (Fabric)

Client-side badge renderer for verified NOVEX Minecraft identities.

## Current build targets

- Minecraft Java 1.21.1 — Fabric Loader 0.16.10
- Minecraft Java 1.21.4 — Fabric Loader 0.16.10
- Minecraft Java 1.21.5 — Fabric Loader 0.16.14
- Minecraft Java 1.21.8 — Fabric Loader 0.17.3
- Java 21

Each Minecraft version is compiled against its matching Yarn mappings and has its own jar. This is not a claim of compatibility with every version supported by the launcher; more versions must pass the same build and runtime checks before being added.

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

## Launcher integration and privacy

The Windows nightly build compiles the four supported jars into NOVEX. On launch, the launcher installs the matching jar for supported Fabric versions without overwriting an existing file. The mod does not make badge requests unless the launcher has written a local consent marker after the user accepts the updated privacy notice. Declining the notice removes that marker.

The mod uses Fabric Loader and Minecraft classes only; it does not require Fabric API. Plus entitlement administration and end-to-end multiplayer/runtime testing still need completion. Do not advertise badges as fully verified until those tests pass.
