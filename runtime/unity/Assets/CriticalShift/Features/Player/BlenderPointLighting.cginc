#ifndef CRITICAL_SHIFT_BLENDER_POINT_LIGHTING_INCLUDED
#define CRITICAL_SHIFT_BLENDER_POINT_LIGHTING_INCLUDED
#include "AutoLight.cginc"

// Generated identity cookies distinguish source-physical mine points from other
// rooms' existing lights. RGB carries a signature and the authored emitter radius;
// alpha retains Unity's cookie transmission. Static and moving receivers use the
// same Forward lighting path, including cookies and shadow/probe occlusion.
#if defined(POINT_COOKIE)
#undef UNITY_LIGHT_ATTENUATION
#define UNITY_LIGHT_ATTENUATION(destName,input,worldPos) \
    DECLARE_LIGHT_COORD(input,worldPos); \
    float4 csCookie=texCUBE(_LightTexture0,lightCoord); \
    float csLegacy=tex2D(_LightTextureB0,dot(lightCoord,lightCoord).rr).r; \
    bool csPhysical=abs(csCookie.r-.9375)<.001 && abs(csCookie.g-.03125)<.001; \
    float3 csToLight=_WorldSpaceLightPos0.xyz-worldPos; \
    float csRadius=max(csCookie.b,.001); \
    float csRadial=csPhysical ? rcp(dot(csToLight,csToLight)+csRadius*csRadius) : csLegacy; \
    float destName=csRadial*csCookie.a*UNITY_SHADOW_ATTENUATION(input,worldPos);
#endif
#endif
