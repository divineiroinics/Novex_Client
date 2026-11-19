package org.xirx.novexbadge;

import net.minecraft.text.Text;
import net.minecraft.text.MutableText;
import net.minecraft.util.Formatting;
import net.minecraft.util.Identifier;
import java.lang.reflect.Constructor;
import java.lang.reflect.Method;

public final class BadgeText {
    private static final Identifier BADGE_FONT = createBadgeFont();

    private BadgeText() {}


    // 1.21.9 introduced StyleSpriteSource.Font; earlier releases still take
    // Identifier directly. Reflection lets the same mapped source compile for both.
    private static Style withBadgeFont(Style style) {
        try {
            Class<?> sourceType = Class.forName("net.minecraft.text.StyleSpriteSource");
            Class<?> fontType = Class.forName("net.minecraft.text.StyleSpriteSource$Font");
            Object fontSource = fontType.getConstructor(Identifier.class).newInstance(BADGE_FONT);
            Method withFont = Style.class.getMethod("withFont", sourceType);
            return (Style) withFont.invoke(style, fontSource);
        } catch (ClassNotFoundException | NoSuchMethodException olderApi) {
            try {
                Method withFont = Style.class.getMethod("withFont", Identifier.class);
                return (Style) withFont.invoke(style, BADGE_FONT);
            } catch (ReflectiveOperationException error) {
                throw new IllegalStateException("Could not apply NOVEX badge font", error);
            }
        } catch (ReflectiveOperationException error) {
            throw new IllegalStateException("Could not apply NOVEX badge font", error);
        }
    }

    // Identifier.of is used by current Minecraft versions; older 1.x versions
    // expose the same constructor instead. Reflection keeps one source compatible
    // across both APIs without changing the identifier value.
    private static Identifier createBadgeFont() {
        try {
            Method factory = Identifier.class.getMethod("of", String.class, String.class);
            return (Identifier) factory.invoke(null, "novex_badges", "badge");
        } catch (NoSuchMethodException ignored) {
            try {
                Constructor<Identifier> constructor =
                        Identifier.class.getDeclaredConstructor(String.class, String.class);
                constructor.setAccessible(true);
                return constructor.newInstance("novex_badges", "badge");
            } catch (ReflectiveOperationException error) {
                throw new IllegalStateException("Could not create NOVEX badge font identifier", error);
            }
        } catch (ReflectiveOperationException error) {
            throw new IllegalStateException("Could not create NOVEX badge font identifier", error);
        }
    }

    /** Adds the NOVEX client mark to this installation's own player name. */
    public static Text prependNovexLogo(Text original) {
        if (original == null) return null;
        MutableText marker = Text.literal("\uE001")
                .styled(style -> withBadgeFont(style).withColor(Formatting.RED));
        return marker.append(Text.literal(" ")).append(original.copy());
    }

    /** Adds a verified membership badge to a player's name. */
    public static Text prepend(Text original, Badge badge) {
        if (original == null || badge == null) return original;

        Formatting iconColor = badge == Badge.PLUS ? Formatting.GOLD : Formatting.RED;
        MutableText marker = Text.literal("\uE001")
                .styled(style -> withBadgeFont(style).withColor(iconColor));
        if (badge == Badge.PLUS) {
            marker.append(Text.literal("+").formatted(Formatting.AQUA));
        }
        return marker.append(Text.literal(" ")).append(original.copy());
    }
}
