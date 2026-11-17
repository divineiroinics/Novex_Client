package org.xirx.novexbadge.mixin;

import net.minecraft.entity.Entity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.text.Text;
import org.xirx.novexbadge.Badge;
import org.xirx.novexbadge.BadgeCache;
import org.xirx.novexbadge.BadgeText;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(Entity.class)
abstract class EntityDisplayNameMixin {
    @Inject(method = "getDisplayName", at = @At("RETURN"), cancellable = true)
    private void novex$appendVerifiedBadge(CallbackInfoReturnable<Text> cir) {
        Entity entity = (Entity) (Object) this;
        if (!(entity instanceof PlayerEntity player)) return;

        Badge badge = BadgeCache.get(player.getUuid());
        if (badge != null) {
            cir.setReturnValue(BadgeText.prepend(cir.getReturnValue(), badge));
        }
    }
}
