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

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return reply({ error: "method_not_allowed" }, 405);

  let body: unknown;
  try { body = await req.json(); }
  catch { return reply({ error: "invalid_json" }, 400); }

  const uuid = (body as { minecraft_uuid?: unknown })?.minecraft_uuid;
  if (typeof uuid !== "string" ||
      !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(uuid)) {
    return reply({ error: "invalid_minecraft_uuid" }, 400);
  }

  const projectUrl = Deno.env.get("SUPABASE_URL");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!projectUrl || !serviceKey) return reply({ error: "service_unavailable" }, 503);

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
