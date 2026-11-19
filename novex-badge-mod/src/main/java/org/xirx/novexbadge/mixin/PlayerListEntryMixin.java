package org.xirx.novexbadge.mixin;

import net.minecraft.client.MinecraftClient;
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
    private void novex$appendNovexBranding(CallbackInfoReturnable<Text> cir) {
        PlayerListEntry entry = (PlayerListEntry) (Object) this;
        Text original = cir.getReturnValue();
        // Vanilla returns null when the server has not supplied a custom
        // display name, so use the profile name as the fallback.
        if (original == null) {
            original = Text.literal(entry.getProfile().getName());
        }

        MinecraftClient client = MinecraftClient.getInstance();
        if (client.player != null
                && client.player.getUuid().equals(entry.getProfile().getId())) {
            cir.setReturnValue(BadgeText.prependNovexLogo(original));
            return;
        }

        Badge badge = BadgeCache.get(entry.getProfile().getId());
        if (badge != null) {
            cir.setReturnValue(BadgeText.prepend(original, badge));
        }
    }
}
