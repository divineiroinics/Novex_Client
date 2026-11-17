package org.xirx.novexbadge;

import net.fabricmc.api.ClientModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class NovexBadgesClient implements ClientModInitializer {
    public static final String MOD_ID = "novex_badges";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitializeClient() {
        LOGGER.info("NOVEX Badges loaded. Verified badge lookups are performed asynchronously.");
    }
}
