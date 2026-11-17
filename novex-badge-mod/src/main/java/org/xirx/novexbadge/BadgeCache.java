package org.xirx.novexbadge;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;

public final class BadgeCache {
    private static final String LOOKUP_URL =
            "https://epsqlgboxuwbfedqhuax.supabase.co/functions/v1/novex-badge-lookup";
    private static final long CACHE_MILLIS = 90_000L;
    private static final HttpClient HTTP = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(3))
            .build();

    private record CachedBadge(Badge badge, long expiresAt) {}

    private static final ConcurrentHashMap<UUID, CachedBadge> CACHE = new ConcurrentHashMap<>();
    private static final ConcurrentHashMap<UUID, Long> LAST_REQUEST = new ConcurrentHashMap<>();

    private BadgeCache() {}

    public static Badge get(UUID playerId) {
        long now = System.currentTimeMillis();
        CachedBadge cached = CACHE.get(playerId);
        if (cached != null && cached.expiresAt() > now) {
            return cached.badge();
        }

        Long last = LAST_REQUEST.get(playerId);
        if (last == null || now - last > CACHE_MILLIS) {
            if (LAST_REQUEST.putIfAbsent(playerId, now) == null ||
                    now - LAST_REQUEST.getOrDefault(playerId, now) > CACHE_MILLIS) {
                LAST_REQUEST.put(playerId, now);
                lookup(playerId);
            }
        }
        return null;
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
