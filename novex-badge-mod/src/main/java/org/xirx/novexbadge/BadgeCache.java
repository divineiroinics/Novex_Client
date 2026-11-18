package org.xirx.novexbadge;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.UUID;
import java.nio.file.Files;
import java.nio.file.Path;

import net.fabricmc.loader.api.FabricLoader;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

public final class BadgeCache {
    private static final String LOOKUP_URL =
            "https://epsqlgboxuwbfedqhuax.supabase.co/functions/v1/novex-badge-lookup";
    private static final long CACHE_MILLIS = 90_000L;
    private static final int CLEANUP_EVERY = 128;
    // No network lookup occurs unless the launcher wrote an explicit consent
    // marker after the user accepted the NOVEX privacy notice.
    private static final boolean CONSENTED = readConsent();
    private static final HttpClient HTTP = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(3))
            .build();

    private record CachedBadge(Badge badge, long expiresAt) {}

    private static final ConcurrentHashMap<UUID, CachedBadge> CACHE = new ConcurrentHashMap<>();
    private static final ConcurrentHashMap<UUID, Long> LAST_REQUEST = new ConcurrentHashMap<>();
    private static final AtomicInteger LOOKUP_COUNT = new AtomicInteger();

    private BadgeCache() {}

    public static Badge get(UUID playerId) {
        long now = System.currentTimeMillis();
        CachedBadge cached = CACHE.get(playerId);
        if (cached != null) {
            if (cached.expiresAt() > now) return cached.badge();
            CACHE.remove(playerId, cached);
        }

        // compute() makes the per-player cooldown atomic. The previous
        // putIfAbsent/get sequence could race and issue duplicate requests
        // when several name render calls arrived in the same frame.
        AtomicBoolean shouldLookup = new AtomicBoolean(false);
        LAST_REQUEST.compute(playerId, (id, last) -> {
            if (last == null || now - last >= CACHE_MILLIS) {
                shouldLookup.set(true);
                return now;
            }
            return last;
        });

        if (shouldLookup.get()) lookup(playerId);

        // Keep UUIDs for players who have left servers from accumulating
        // forever in long-running client sessions.
        if (LOOKUP_COUNT.incrementAndGet() % CLEANUP_EVERY == 0) {
            long cutoff = now - (CACHE_MILLIS * 2);
            CACHE.entrySet().removeIf(entry -> entry.getValue().expiresAt() <= now);
            LAST_REQUEST.entrySet().removeIf(entry -> entry.getValue() < cutoff);
        }

        return null;
    }


    private static boolean readConsent() {
        try {
            Path marker = FabricLoader.getInstance().getGameDir().resolve("novex-badges-consent.json");
            if (!Files.isRegularFile(marker)) return false;
            JsonObject value = JsonParser.parseString(Files.readString(marker)).getAsJsonObject();
            return value.has("enabled") && value.get("enabled").getAsBoolean()
                    && value.has("policy_version") && value.get("policy_version").getAsInt() >= 2;
        } catch (Exception ignored) {
            return false;
        }
    }

    private static void lookup(UUID playerId) {
        String json = "{\"minecraft_uuid\":\"" + playerId + "\"}";
        HttpRequest request = HttpRequest.newBuilder(URI.create(LOOKUP_URL))
                .timeout(Duration.ofSeconds(5))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();

        CompletableFuture<HttpResponse<String>> future =
                HTTP.sendAsync(request, HttpResponse.BodyHandlers.ofString());
        future.thenAccept(response -> {
            if (response.statusCode() != 200) return;
            try {
                JsonObject result = JsonParser.parseString(response.body()).getAsJsonObject();
                if (!result.has("registered") || !result.get("registered").getAsBoolean()) {
                    CACHE.put(playerId, new CachedBadge(null, System.currentTimeMillis() + CACHE_MILLIS));
                    return;
                }
                Badge badge = "plus".equalsIgnoreCase(result.get("tier").getAsString())
                        ? Badge.PLUS : Badge.STANDARD;
                CACHE.put(playerId, new CachedBadge(badge, System.currentTimeMillis() + CACHE_MILLIS));
            } catch (RuntimeException ignored) {
                // A malformed or unexpected response is treated as unknown, never as Plus.
            }
        }).exceptionally(error -> null);
    }
}
