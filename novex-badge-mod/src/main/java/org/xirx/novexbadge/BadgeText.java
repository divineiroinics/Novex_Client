package org.xirx.novexbadge;

import net.minecraft.text.Text;
import net.minecraft.util.Formatting;

public final class BadgeText {
    private BadgeText() {}

    public static Text prepend(Text original, Badge badge) {
        if (original == null || badge == null) return original;

        Text marker;
        if (badge == Badge.PLUS) {
            marker = Text.literal("✦").formatted(Formatting.GOLD)
                    .append(Text.literal("+").formatted(Formatting.AQUA));
        } else {
            marker = Text.literal("✦").formatted(Formatting.RED);
        }
        return marker.append(Text.literal(" ")).append(original.copy());
    }
}
