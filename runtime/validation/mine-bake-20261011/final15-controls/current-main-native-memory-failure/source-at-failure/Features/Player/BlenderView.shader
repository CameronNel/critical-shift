Shader "Hidden/CriticalShift/BlenderView"
{
    Properties { _MainTex ("Scene", 2D) = "white" {} _ViewLut ("Blender display transform", 2D) = "white" {} }
    SubShader
    {
        Cull Off ZWrite Off ZTest Always
        Pass
        {
            CGPROGRAM
            #pragma vertex vert_img
            #pragma fragment frag
            #include "UnityCG.cginc"
            sampler2D _MainTex, _ViewLut;
            float4 frag(v2f_img i) : SV_Target
            {
                float3 scene = max(tex2D(_MainTex,i.uv).rgb, exp2(-12.0));
                float3 coord = saturate((log2(scene)+12.0)/18.0)*63.0;
                float blue = floor(coord.b);
                float2 low = float2((blue*64.0+coord.r+0.5)/4096.0,(coord.g+0.5)/64.0);
                float2 high = float2((min(blue+1.0,63.0)*64.0+coord.r+0.5)/4096.0,low.y);
                return float4(lerp(tex2Dlod(_ViewLut,float4(low,0,0)).rgb,tex2Dlod(_ViewLut,float4(high,0,0)).rgb,frac(coord.b)),1);
            }
            ENDCG
        }
    }
    Fallback Off
}
