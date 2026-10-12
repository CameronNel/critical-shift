#ifndef CS_DIAGNOSTIC_PHYSICAL_POINT_INCLUDED
#define CS_DIAGNOSTIC_PHYSICAL_POINT_INCLUDED
#include "AutoLight.cginc"
#if defined(POINT_COOKIE)
#undef UNITY_LIGHT_ATTENUATION
// Diagnostic identity-cookie RGB encodes a signature and emitter radius;
// alpha preserves stock cookie transmission. Other light cookies stay stock.
#define UNITY_LIGHT_ATTENUATION(destName,input,worldPos) \
 DECLARE_LIGHT_COORD(input,worldPos); \
 float4 csCookie=texCUBE(_LightTexture0,lightCoord); \
 float csLegacy=tex2D(_LightTextureB0,dot(lightCoord,lightCoord).rr).r; \
 float csIsPhysical=abs(csCookie.r-.9375)<.001 && abs(csCookie.g-.03125)<.001; \
 float3 csToLight=_WorldSpaceLightPos0.xyz-worldPos; \
 float csRadius=max(csCookie.b,.001); \
 float csRadial=csIsPhysical ? rcp(max(dot(csToLight,csToLight),csRadius*csRadius)) : csLegacy; \
 float destName=csRadial*csCookie.a*UNITY_SHADOW_ATTENUATION(input,worldPos);
#endif
#endif
