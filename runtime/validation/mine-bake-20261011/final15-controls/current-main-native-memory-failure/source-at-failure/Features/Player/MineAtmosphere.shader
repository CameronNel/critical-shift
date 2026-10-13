
Shader "Hidden/CriticalShift/MineAtmosphere"
{
    Properties { _MainTex("Scene",2D)="white"{} }
    SubShader
    {
        Cull Off ZWrite Off ZTest Always
        Pass
        {
            CGPROGRAM
            #pragma vertex vert_img
            #pragma fragment frag
            #pragma target 3.0
            #include "UnityCG.cginc"
            sampler2D _MainTex,_CameraDepthTexture,_Density0,_Density1,_Lighting0,_Lighting1;
            float4x4 _InvProjection,_MineCameraToWorld;
            float3 _Origin,_Minimum0,_Maximum0,_Minimum1,_Maximum1,_Grid0,_Grid1;
            float4 _Scatter0,_Scatter1;int _VolumeCount;
            float3 sampleGrid(sampler2D atlas,float3 uv,float3 grid)
            {
                uv=clamp(uv,0.5/grid,1-0.5/grid);
                float z=uv.z*grid.z-.5;float low=floor(z);float f=z-low;
                float2 a=float2(uv.x,(low+uv.y)/grid.z);
                float2 b=float2(uv.x,(min(low+1,grid.z-1)+uv.y)/grid.z);
                return lerp(tex2Dlod(atlas,float4(a,0,0)).rgb,tex2Dlod(atlas,float4(b,0,0)).rgb,f);
            }
            float3 integrate(float3 scene,float3 direction,float distance,float3 minimum,float3 maximum,
                float3 grid,float3 scatter,sampler2D density,sampler2D lighting)
            {
                float3 safeDirection=direction+float3(abs(direction.x)<1e-6?1e-6:0,abs(direction.y)<1e-6?1e-6:0,abs(direction.z)<1e-6?1e-6:0);
                float3 a=(minimum-_Origin)/safeDirection,b=(maximum-_Origin)/safeDirection;
                float3 entry=min(a,b),exit=max(a,b);
                float start=max(0,max(entry.x,max(entry.y,entry.z)));
                float end=min(distance,min(exit.x,min(exit.y,exit.z)));
                if(end<=start)return scene;
                float step=(end-start)/32;float transmission=1;float3 radiance=0;
                [loop] for(int i=0;i<32;i++)
                {
                    float3 uv=(_Origin+direction*(start+(i+.5)*step)-minimum)/(maximum-minimum);
                    float sigma=max(0,sampleGrid(density,uv.xzy,grid).r);
                    float attenuation=exp(-sigma*step);
                    radiance+=transmission*(1-attenuation)*scatter*max(0,sampleGrid(lighting,uv.xzy,float3(32,4,4)));
                    transmission*=attenuation;
                }
                return scene*transmission+radiance;
            }
            float4 frag(v2f_img input):SV_Target
            {
                float4 scene=tex2D(_MainTex,input.uv);
                float4 view=mul(_InvProjection,float4(input.uv*2-1,1,1));
                float3 ray=normalize(view.xyz/view.w);
                float3 direction=normalize(mul((float3x3)_MineCameraToWorld,ray));
                float distance=LinearEyeDepth(SAMPLE_DEPTH_TEXTURE(_CameraDepthTexture,input.uv))/max(abs(ray.z),1e-6);
                if(_VolumeCount>0)scene.rgb=integrate(scene.rgb,direction,distance,_Minimum0,_Maximum0,_Grid0,_Scatter0.rgb,_Density0,_Lighting0);
                if(_VolumeCount>1)scene.rgb=integrate(scene.rgb,direction,distance,_Minimum1,_Maximum1,_Grid1,_Scatter1.rgb,_Density1,_Lighting1);
                return scene;
            }
            ENDCG
        }
    }
}
