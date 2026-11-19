package org.xirx.novexbadge.modern.mixin;

import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import org.xirx.novexbadge.Badge;
import org.xirx.novexbadge.BadgeCache;
import org.xirx.novexbadge.modern.BadgeText;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(Entity.class)
abstract class EntityDisplayNameMixin {
    @Inject(method = "getDisplayName", at = @At("RETURN"), cancellable = true)
    private void novex$appendNovexBranding(CallbackInfoReturnable<Component> cir) {
        Entity entity = (Entity) (Object) this;
        if (!(entity instanceof Player player)) return;

        Minecraft client = Minecraft.getInstance();
        if (client.player != null && client.player.getUUID().equals(player.getUUID())) {
            cir.setReturnValue(BadgeText.prependNovexLogo(cir.getReturnValue()));
            return;
        }

        Badge badge = BadgeCache.get(player.getUUID());
        if (badge != null) {
            cir.setReturnValue(BadgeText.prepend(cir.getReturnValue(), badge));
        }
    }
}
