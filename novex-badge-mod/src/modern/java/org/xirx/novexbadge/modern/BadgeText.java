package org.xirx.novexbadge.modern;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.Style;
import net.minecraft.resources.ResourceLocation;
import org.xirx.novexbadge.Badge;

public final class BadgeText {
    private static final ResourceLocation BADGE_FONT =
            ResourceLocation.fromNamespaceAndPath("novex_badges", "badge");

    private BadgeText() {}

    /** Adds the NOVEX client mark to this installation's own player name. */
    public static Component prependNovexLogo(Component original) {
        if (original == null) return null;
        MutableComponent marker = Component.literal("\uE001")
                .withStyle(Style.EMPTY.withFont(BADGE_FONT).withColor(ChatFormatting.RED));
        return marker.append(Component.literal(" ")).append(original);
    }

    /** Adds a verified membership badge to a player's name. */
    public static Component prepend(Component original, Badge badge) {
        if (original == null || badge == null) return original;

        ChatFormatting iconColor = badge == Badge.PLUS ? ChatFormatting.GOLD : ChatFormatting.RED;
        MutableComponent marker = Component.literal("\uE001")
                .withStyle(Style.EMPTY.withFont(BADGE_FONT).withColor(iconColor));
        if (badge == Badge.PLUS) {
            marker.append(Component.literal("+").withStyle(ChatFormatting.AQUA));
        }
        return marker.append(Component.literal(" ")).append(original);
    }
}
