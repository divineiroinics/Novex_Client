package org.xirx.novexbadge.mixin;

import net.minecraft.client.MinecraftClient;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.text.Text;
import org.xirx.novexbadge.Badge;
import org.xirx.novexbadge.BadgeCache;
import org.xirx.novexbadge.BadgeText;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(PlayerEntity.class)
abstract class EntityDisplayNameMixin {
    @Inject(method = "getDisplayName", at = @At("RETURN"), cancellable = true)
    private void novex$appendNovexBranding(CallbackInfoReturnable<Text> cir) {
        PlayerEntity player = (PlayerEntity) (Object) this;

        // Brand only this client installation's own player name. Other players
        // receive a marker only when their Minecraft identity is verified.
        MinecraftClient client = MinecraftClient.getInstance();
        if (client.player != null && client.player.getUuid().equals(player.getUuid())) {
            cir.setReturnValue(BadgeText.prependNovexLogo(cir.getReturnValue()));
            return;
        }

        Badge badge = BadgeCache.get(player.getUuid());
        if (badge != null) {
            cir.setReturnValue(BadgeText.prepend(cir.getReturnValue(), badge));
        }
    }
}
