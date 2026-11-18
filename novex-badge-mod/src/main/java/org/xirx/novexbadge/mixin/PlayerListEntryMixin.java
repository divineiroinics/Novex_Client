package org.xirx.novexbadge.mixin;

import net.minecraft.client.network.PlayerListEntry;
import net.minecraft.text.Text;
import org.xirx.novexbadge.Badge;
import org.xirx.novexbadge.BadgeCache;
import org.xirx.novexbadge.BadgeText;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(PlayerListEntry.class)
abstract class PlayerListEntryMixin {
    @Inject(method = "getDisplayName", at = @At("RETURN"), cancellable = true)
    private void novex$appendVerifiedBadge(CallbackInfoReturnable<Text> cir) {
        PlayerListEntry entry = (PlayerListEntry) (Object) this;
        Badge badge = BadgeCache.get(entry.getProfile().getId());
        if (badge != null) {
            // Vanilla returns null when the server has not supplied a custom
            // display name. The tab list then falls back to the profile name,
            // so build that fallback here before adding the badge.
            Text original = cir.getReturnValue();
            if (original == null) {
                original = Text.literal(entry.getProfile().getName());
            }
            cir.setReturnValue(BadgeText.prepend(original, badge));
        }
    }
}
