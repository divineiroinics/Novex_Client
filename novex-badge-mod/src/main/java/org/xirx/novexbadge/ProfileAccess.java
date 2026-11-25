package org.xirx.novexbadge;

import com.mojang.authlib.GameProfile;
import java.lang.reflect.Method;
import java.util.UUID;

/** Bridges Authlib's getter-to-record accessor change across Minecraft releases. */
public final class ProfileAccess {
    private ProfileAccess() {}

    public static UUID id(GameProfile profile) {
        Object value = invokeAccessor(profile, "getId", "id");
        return value instanceof UUID uuid ? uuid : null;
    }

    public static String name(GameProfile profile) {
        Object value = invokeAccessor(profile, "getName", "name");
        return value instanceof String name ? name : "";
    }

    private static Object invokeAccessor(GameProfile profile, String legacy, String modern) {
        if (profile == null) return null;
        for (String methodName : new String[] { legacy, modern }) {
            try {
                Method method = profile.getClass().getMethod(methodName);
                return method.invoke(profile);
            } catch (NoSuchMethodException ignored) {
                // Try the accessor used by the other Authlib generation.
            } catch (ReflectiveOperationException error) {
                throw new IllegalStateException("Could not read player profile " + methodName, error);
            }
        }
        return null;
    }
}
