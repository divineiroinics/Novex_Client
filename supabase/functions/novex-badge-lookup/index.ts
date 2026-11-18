import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

function reply(body: unknown, status = 200, cache = "no-store") {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      ...corsHeaders,
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": cache,
      "X-Content-Type-Options": "nosniff",
    },
  });
}

function canonicalUuid(raw: string): string {
  const value = raw.toLowerCase().replace(/-/g, "");
  return value.length === 32
    ? `${value.slice(0, 8)}-${value.slice(8, 12)}-${value.slice(12, 16)}-${value.slice(16, 20)}-${value.slice(20)}`
    : "";
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return reply({ error: "method_not_allowed" }, 405);

  const declaredLength = Number(req.headers.get("content-length") ?? "0");
  if (Number.isFinite(declaredLength) && declaredLength > 12_288) {
    return reply({ error: "request_too_large" }, 413);
  }

  let body: unknown;
  try {
    const rawBody = await req.text();
    if (rawBody.length > 12_288) return reply({ error: "request_too_large" }, 413);
    body = JSON.parse(rawBody);
  } catch {
    return reply({ error: "invalid_json" }, 400);
  }

  const input = body as {
    action?: unknown;
    minecraft_uuid?: unknown;
    minecraft_access_token?: unknown;
  };

  const projectUrl = Deno.env.get("SUPABASE_URL");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!projectUrl || !serviceKey) return reply({ error: "service_unavailable" }, 503);

  const action = input?.action === "verify" ? "verify" : "lookup";
  // Supabase's edge proxy supplies the client address. Hash it before sending
  // it to the database; the raw address is never persisted.
  const forwardedChain = req.headers.get("x-forwarded-for")?.split(",");
  const forwarded = forwardedChain?.at(-1)?.trim();
  const clientAddress = req.headers.get("cf-connecting-ip") ||
    req.headers.get("x-real-ip") || forwarded || "unknown";
  const addressBytes = new TextEncoder().encode(clientAddress);
  const addressHash = await crypto.subtle.digest("SHA-256", addressBytes);
  const keyHash = Array.from(new Uint8Array(addressHash))
    .map((byte) => byte.toString(16).padStart(2, "0")).join("");
  try {
    const limitResponse = await fetch(`${projectUrl}/rest/v1/rpc/novex_consume_badge_rate_limit`, {
      method: "POST",
      headers: {
        "apikey": serviceKey,
        "Authorization": `Bearer ${serviceKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        p_key_hash: keyHash,
        p_action: action,
        p_limit: action === "verify" ? 5 : 120,
        p_window_seconds: action === "verify" ? 3600 : 60,
      }),
      signal: AbortSignal.timeout(5_000),
    });
    if (!limitResponse.ok) return reply({ error: "rate_limit_unavailable" }, 503);
    const allowed = await limitResponse.json();
    if (allowed !== true) {
      return reply({ error: "rate_limit_exceeded" }, 429, "no-store");
    }
  } catch {
    // Fail closed: a database outage must not turn off the protection.
    return reply({ error: "rate_limit_unavailable" }, 503);
  }

  if (input?.action === "verify") {
    const token = input.minecraft_access_token;
    if (typeof token !== "string" || token.length < 20 || token.length > 8192) {
      return reply({ error: "invalid_minecraft_access_token" }, 400);
    }

    try {
      // The token is used only for this upstream profile request and is never
      // written to logs or stored in Supabase.
      const profileResponse = await fetch("https://api.minecraftservices.com/minecraft/profile", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}`, "Accept": "application/json" },
        signal: AbortSignal.timeout(8_000),
      });

      if (profileResponse.status === 401 || profileResponse.status === 403) {
        return reply({ error: "minecraft_token_rejected" }, 401);
      }
      if (!profileResponse.ok) return reply({ error: "minecraft_profile_unavailable" }, 502);

      const profile = await profileResponse.json() as { id?: unknown; name?: unknown };
      if (typeof profile.id !== "string" || !/^[0-9a-f]{32}$/i.test(profile.id) ||
          typeof profile.name !== "string" || !/^[A-Za-z0-9_]{1,16}$/.test(profile.name)) {
        return reply({ error: "invalid_minecraft_profile" }, 502);
      }

      const minecraftUuid = canonicalUuid(profile.id);
      const saved = await fetch(`${projectUrl}/rest/v1/rpc/novex_register_verified_profile`, {
        method: "POST",
        headers: {
          "apikey": serviceKey,
          "Authorization": `Bearer ${serviceKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          p_minecraft_uuid: minecraftUuid,
          p_minecraft_username: profile.name,
        }),
        signal: AbortSignal.timeout(8_000),
      });
      if (!saved.ok) return reply({ error: "verification_save_failed" }, 502);

      return reply({
        verified: true,
        minecraft_uuid: minecraftUuid,
        minecraft_username: profile.name,
        method: "minecraft_services_profile",
      });
    } catch {
      return reply({ error: "verification_unavailable" }, 503);
    }
  }

  const uuid = input?.minecraft_uuid;
  if (typeof uuid !== "string" ||
      !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(uuid)) {
    return reply({ error: "invalid_minecraft_uuid" }, 400);
  }

  try {
    const response = await fetch(`${projectUrl}/rest/v1/rpc/novex_lookup_badge`, {
      method: "POST",
      headers: {
        "apikey": serviceKey,
        "Authorization": `Bearer ${serviceKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ p_minecraft_uuid: uuid }),
    });
    if (!response.ok) return reply({ error: "lookup_failed" }, 502);

    const rows = await response.json();
    const identity = Array.isArray(rows) ? rows[0] : null;
    if (!identity) return reply({ registered: false }, 200, "public, max-age=30, s-maxage=30");

    return reply({
      registered: true,
      minecraft_uuid: identity.minecraft_uuid,
      minecraft_username: identity.minecraft_username,
      tier: identity.tier === "plus" ? "plus" : "standard",
    }, 200, "public, max-age=30, s-maxage=30");
  } catch {
    return reply({ error: "service_unavailable" }, 503);
  }
});
