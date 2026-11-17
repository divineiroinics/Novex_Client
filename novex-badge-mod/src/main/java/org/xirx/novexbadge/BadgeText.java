package org.xirx.novexbadge;

import net.minecraft.text.Text;
import net.minecraft.text.MutableText;
import net.minecraft.util.Formatting;
import net.minecraft.util.Identifier;

public final class BadgeText {
    private static final Identifier BADGE_FONT = Identifier.of("novex_badges", "badge");

    private BadgeText() {}

    public static Text prepend(Text original, Badge badge) {
        if (original == null || badge == null) return original;

        Formatting iconColor = badge == Badge.PLUS ? Formatting.GOLD : Formatting.RED;
        MutableText marker = Text.literal("\uE001")
                .styled(style -> style.withFont(BADGE_FONT).withColor(iconColor));
        if (badge == Badge.PLUS) {
            marker.append(Text.literal("+").formatted(Formatting.AQUA));
        }
        return marker.append(Text.literal(" ")).append(original.copy());
    }
}