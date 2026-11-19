package org.xirx.novexbadge.modern.mixin;

import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.PlayerInfo;
import net.minecraft.network.chat.Component;
import java.util.UUID;
import org.xirx.novexbadge.Badge;
import org.xirx.novexbadge.BadgeCache;
import org.xirx.novexbadge.ProfileAccess;
import org.xirx.novexbadge.modern.BadgeText;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(PlayerInfo.class)
abstract class PlayerListEntryMixin {
    @Inject(method = "getTabListDisplayName", at = @At("RETURN"), cancellable = true)
    private void novex$appendNovexBranding(CallbackInfoReturnable<Component> cir) {
        PlayerInfo entry = (PlayerInfo) (Object) this;
        Component original = cir.getReturnValue();
        // Vanilla falls back to the profile name when no custom tab name exists.
        if (original == null) {
            original = Component.literal(ProfileAccess.name(entry.getProfile()));
        }

        UUID profileId = ProfileAccess.id(entry.getProfile());
        if (profileId == null) return;

        Minecraft client = Minecraft.getInstance();
        if (client.player != null && client.player.getUUID().equals(profileId)) {
            cir.setReturnValue(BadgeText.prependNovexLogo(original));
            return;
        }

        Badge badge = BadgeCache.get(profileId);
        if (badge != null) {
            cir.setReturnValue(BadgeText.prepend(original, badge));
        }
    }
}
