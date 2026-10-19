// Night sky for URP: real star field and Milky Way (NASA SVS Deep Star Maps), a lit Moon (NASA CGI Moon Kit), atmospheric extinction,
// twinkle and a moonlit sky glow, in one skybox pass. Sky rotation, Moon and Sun directions come from NightSky.cs as globals; without that
// component the material still renders a fixed sky (handy in the material preview). Maths and defaults: Content/Sky/README.md.
Shader "CriticalShift/NightSky"
{
    Properties
    {
        [NoScaleOffset] _StarCube ("Stars (lat-long cubemap)", Cube) = "black" {}
        [NoScaleOffset] _MilkyWayCube ("Milky Way (lat-long cubemap)", Cube) = "black" {}
        [NoScaleOffset] _MoonColor ("Moon colour", 2D) = "grey" {}
        [NoScaleOffset] _MoonNormal ("Moon normals (linear)", 2D) = "bump" {}

        [Header(Stars)]
        _StarBrightness ("Star brightness", Range(0, 4)) = 1.4
        _StarContrast ("Star contrast (hides the faintest stars)", Range(1, 2)) = 1.25
        _MilkyWayBrightness ("Milky Way brightness", Range(0, 2)) = 0.6
        _TwinkleStrength ("Twinkle strength", Range(0, 1)) = 0.45
        _TwinkleSpeed ("Twinkle speed", Range(0, 20)) = 7
        _Extinction ("Extinction per airmass (RGB)", Vector) = (0.11, 0.17, 0.30, 0)

        [Header(Sky)]
        _ZenithColor ("Sky colour", Color) = (0.20, 0.27, 0.42, 1)
        _ZenithBrightness ("Sky brightness", Range(0, 0.05)) = 0.006
        _HorizonColor ("Horizon glow colour", Color) = (0.42, 0.40, 0.36, 1)
        _HorizonBrightness ("Horizon glow brightness", Range(0, 0.1)) = 0.01
        _GroundColor ("Below the horizon", Color) = (0.012, 0.013, 0.016, 1)

        [Header(Moon)]
        _MoonDiameter ("Moon diameter (degrees; the real Moon is 0.52)", Range(0.3, 5)) = 1.0
        _MoonBrightness ("Moon brightness", Range(0, 8)) = 2.2
        _MoonRelief ("Moon relief", Range(0, 1)) = 1
        _Earthshine ("Earthshine (dark side)", Range(0, 0.1)) = 0.012
        _MoonHalo ("Halo around the Moon", Range(0, 1)) = 0.12
        _MoonHaloSize ("Halo size (degrees)", Range(0.5, 20)) = 3
        _MoonSkyColor ("Moonlit sky colour", Color) = (0.32, 0.45, 0.75, 1)
        _MoonSkyBrightness ("Moonlit sky brightness", Range(0, 0.1)) = 0.02
        _MoonWashout ("Milky Way washed out by the Moon", Range(0, 10)) = 1.2
    }

    SubShader
    {
        Tags { "Queue" = "Background" "RenderType" = "Background" "PreviewType" = "Skybox" "RenderPipeline" = "UniversalPipeline" }
        Cull Off
        ZWrite Off

        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 3.5
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            TEXTURECUBE(_StarCube);     SAMPLER(sampler_StarCube);
            TEXTURECUBE(_MilkyWayCube); SAMPLER(sampler_MilkyWayCube);
            TEXTURE2D(_MoonColor);      SAMPLER(sampler_MoonColor);
            TEXTURE2D(_MoonNormal);     SAMPLER(sampler_MoonNormal);

            CBUFFER_START(UnityPerMaterial)
                float _StarBrightness, _StarContrast, _MilkyWayBrightness, _TwinkleStrength, _TwinkleSpeed;
                float4 _Extinction;
                float4 _ZenithColor, _HorizonColor, _GroundColor;
                float _ZenithBrightness, _HorizonBrightness;
                float _MoonDiameter, _MoonBrightness, _MoonRelief, _Earthshine, _MoonHalo, _MoonHaloSize;
                float4 _MoonSkyColor;
                float _MoonSkyBrightness, _MoonWashout;
            CBUFFER_END

            // Set every frame by NightSky.cs (Shader.SetGlobal*). Unset globals read as zero, which the code below treats as "no driver".
            float4x4 _CS_SkyFromWorld;   // world direction -> star map direction (celestial pole on +Y)
            float4 _CS_MoonDir;          // xyz: direction to the Moon (world)
            float4 _CS_MoonNorth;        // xyz: the Moon's north on the sky, perpendicular to _CS_MoonDir
            float4 _CS_SunDir;           // xyz: direction to the Sun (world); lights the Moon, sets its phase
            float4 _CS_SkyTime;          // x: seconds, wrapped, for the twinkle

            struct Attributes { float4 positionOS : POSITION; UNITY_VERTEX_INPUT_INSTANCE_ID };
            struct Varyings { float4 positionCS : SV_POSITION; float3 dirWS : TEXCOORD0; UNITY_VERTEX_OUTPUT_STEREO };

            Varyings vert(Attributes v)
            {
                Varyings o;
                UNITY_SETUP_INSTANCE_ID(v);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                o.positionCS = TransformObjectToHClip(v.positionOS.xyz);
                o.dirWS = v.positionOS.xyz;          // the skybox mesh is centred on the camera: its vertex is the view direction
                return o;
            }

            float Hash13(float3 p)
            {
                p = frac(p * 0.1031);
                p += dot(p, p.zyx + 31.32);
                return frac((p.x + p.y) * p.z);
            }

            float ValueNoise(float3 x)
            {
                float3 i = floor(x), f = frac(x);
                f = f * f * (3.0 - 2.0 * f);
                return lerp(lerp(lerp(Hash13(i), Hash13(i + float3(1, 0, 0)), f.x), lerp(Hash13(i + float3(0, 1, 0)), Hash13(i + float3(1, 1, 0)), f.x), f.y),
                            lerp(lerp(Hash13(i + float3(0, 0, 1)), Hash13(i + float3(1, 0, 1)), f.x), lerp(Hash13(i + float3(0, 1, 1)), Hash13(i + 1.0), f.x), f.y), f.z);
            }

            // Relative optical path through the atmosphere at altitude sinAlt (Kasten and Young 1989); about 38 at the horizon.
            float Airmass(float sinAlt)
            {
                float s = saturate(sinAlt);
                return 1.0 / (s + 0.50572 * pow(degrees(asin(s)) + 6.07995, -1.6364));
            }

            float4 frag(Varyings i) : SV_Target
            {
                float3 d = normalize(i.dirWS);
                float alt = d.y;                                            // sine of the altitude
                float up = max(alt, 0.0);
                float3 transmit = exp(-_Extinction.rgb * Airmass(alt));     // starlight and moonlight dim and redden towards the horizon

                // Moon and Sun (absent when the driver is not running)
                float hasMoon = step(0.5, dot(_CS_MoonDir.xyz, _CS_MoonDir.xyz));
                // Without a driver, park the Moon below the horizon so every term below stays finite (it is masked out anyway).
                float3 m = hasMoon > 0.0 ? _CS_MoonDir.xyz : float3(0.0, -1.0, 0.0);
                float3 north = hasMoon > 0.0 ? _CS_MoonNorth.xyz : float3(0.0, 0.0, 1.0);
                float3 s = hasMoon > 0.0 ? _CS_SunDir.xyz : float3(0.0, 0.0, 1.0);
                float illum = hasMoon * saturate(0.5 + 0.5 * dot(s, -m));    // illuminated fraction: phase angle between the Sun and us, seen from the Moon
                float moonUp = hasMoon * smoothstep(-0.03, 0.05, m.y);
                float cosA = dot(d, m);
                float angle = acos(clamp(cosA, -1.0, 1.0));

                // Sky background: dark blue, brighter towards the horizon (airglow, distant light), lifted and turned blue by the Moon
                float h = 1.0 - up;
                float3 sky = _ZenithColor.rgb * _ZenithBrightness * (1.0 + 2.5 * h * h * h * h)
                           + _HorizonColor.rgb * _HorizonBrightness * exp(-up / 0.06);
                float moonScatter = illum * moonUp * (0.35 + 0.65 * exp(-angle / 0.6)) * (1.0 + h * h);
                sky += _MoonSkyColor.rgb * _MoonSkyBrightness * moonScatter;

                // Stars and Milky Way, looked up in the rotating celestial frame
                float3 c = mul((float3x3)_CS_SkyFromWorld, d);
                c = dot(c, c) > 0.25 ? c : d;
                float3 stars = SAMPLE_TEXTURECUBE(_StarCube, sampler_StarCube, c).rgb;
                float lum = max(max(stars.r, stars.g), stars.b);
                stars *= pow(max(lum, 1e-6), _StarContrast - 1.0);           // faint stars fall away faster than bright ones
                float t = _CS_SkyTime.x * _TwinkleSpeed;
                float n = 0.65 * ValueNoise(c * 700.0 + float3(t, 0.37 * t, -0.53 * t)) + 0.35 * ValueNoise(c * 1500.0 - float3(0.61 * t, t, 0.29 * t));
                stars *= 1.0 + _TwinkleStrength * lerp(0.35, 1.0, h * h) * (2.0 * n - 1.0);   // twinkle grows near the horizon
                float3 milkyWay = SAMPLE_TEXTURECUBE(_MilkyWayCube, sampler_MilkyWayCube, c).rgb * _MilkyWayBrightness;
                milkyWay /= 1.0 + _MoonWashout * illum * moonUp;
                float3 col = sky + (stars * _StarBrightness + milkyWay) * transmit;

                // The Moon: a sphere lit by the Sun, seen as a disc. The near side faces us; its north follows the sky's.
                float radius = radians(_MoonDiameter * 0.5);
                float3 right = cross(north, m);
                float2 p = float2(dot(d, right), dot(d, north)) / (max(cosA, 1e-4) * tan(radius));
                float r = length(p);
                float disc = hasMoon * step(0.0, cosA) * saturate((1.0 - r) / max(fwidth(r), 1e-4));
                float2 q = p * (0.999 / max(r, 1.0));                           // shade inside the disc only: off it, atan2 could see (0, 0) and give NaN
                float3 nGeo = q.x * right + q.y * north - sqrt(1.0 - dot(q, q)) * m;
                float lon = atan2(dot(nGeo, right), dot(nGeo, -m));
                float lat = asin(clamp(dot(nGeo, north), -1.0, 1.0));
                float2 uv = float2(0.5 + lon / TWO_PI, 0.5 + lat / PI);
                float3 albedo = SAMPLE_TEXTURE2D(_MoonColor, sampler_MoonColor, uv).rgb;
                float3 tn = SAMPLE_TEXTURE2D(_MoonNormal, sampler_MoonNormal, uv).xyz * 2.0 - 1.0;
                float3 east = cross(nGeo, north);
                east = dot(east, east) > 1e-6 ? normalize(east) : right;
                float3 nrm = normalize(lerp(nGeo, tn.x * east + tn.y * cross(east, nGeo) + tn.z * nGeo, _MoonRelief * saturate(3.0 * dot(nGeo, -m))));   // relief fades at the limb
                float mu0 = saturate(dot(nrm, s)), mu0Geo = saturate(dot(nGeo, s)), mu = saturate(dot(nGeo, -m));
                // Lommel-Seeliger (the flat-looking full Moon); the geometric term in the denominator keeps the relief from flickering where
                // the terminator meets the limb, and the small constant keeps that corner from blowing up.
                float3 moon = albedo * (_MoonBrightness * 2.05 * mu0 / (mu0Geo + mu + 0.05) + _Earthshine);
                col = lerp(col, moon * transmit + sky, disc);             // the sky's glow is air in front of the Moon

                // Halo: forward scatter close to the Moon
                col += float3(0.95, 0.97, 1.0) * _MoonHalo * illum * moonUp * exp(-max(angle - radius, 0.0) / radians(_MoonHaloSize)) * transmit;

                // Below the horizon
                col = lerp(col, _GroundColor.rgb, smoothstep(0.0, -0.02, alt));
                return float4(col, 1.0);
            }
            ENDHLSL
        }
    }
    Fallback Off
}
