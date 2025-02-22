Shader "Unlit/PathTracingPathTracer"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
        _Resolution ("Resolution", Vector) = (1920,1080,0,0)
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            // Uniforms (set from Material or C#)
            sampler2D _MainTex; // used like iChannel0
            // _Time is provided by Unity (float4 _Time; _Time.x holds the time in seconds)
            float4 _Resolution; // x,y = resolution

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float4 vertex : SV_POSITION;
                float2 uv : TEXCOORD0;
            };

            v2f vert(appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = v.uv;
                return o;
            }

            // Constants
            #define FLT_MAX 3.402823466e+38
            static const float PI  = 3.14159265359;
            static const float PHI = 1.61803398875;

            // Structures
            struct ray {
                float3 A;
                float3 B;
            };

            struct hitRecord {
                float t;
                float3 p;
                float3 normal;
                int mat;
                float3 color;
            };

            struct sphere {
                float3 center;
                float radius;
                int mat;
                float3 color;
            };

            struct hitableList {
                sphere sList[4];
                int size;
            };

            struct camera {
                float3 llc;
                float3 h;
                float3 v;
                float3 o;
            };

            // Utility functions
            float3 origin(ray r) { return r.A; }
            float3 direction(ray r) { return r.B; }
            float3 pointAtParameter(ray r, float t) { return r.A + t * r.B; }

            bool hitSphere(ray r, float tmin, float tmax, inout hitRecord rec, sphere s)
            {
                float3 oc = origin(r) - s.center;
                float a = dot(direction(r), direction(r));
                float b = dot(oc, direction(r));
                float c = dot(oc, oc) - s.radius * s.radius;
                float d = b * b - a * c;
                if (d > 0.0)
                {
                    float temp = (-b - sqrt(b * b - a * c)) / a;
                    if (temp < tmax && temp > tmin)
                    {
                        rec.t = temp;
                        rec.p = pointAtParameter(r, rec.t);
                        rec.normal = (rec.p - s.center) / s.radius;
                        rec.mat = s.mat;
                        rec.color = s.color;
                        return true;
                    }
                    temp = (-b + sqrt(b * b - a * c)) / a;
                    if (temp < tmax && temp > tmin)
                    {
                        rec.t = temp;
                        rec.p = pointAtParameter(r, rec.t);
                        rec.normal = (rec.p - s.center) / s.radius;
                        rec.mat = s.mat;
                        rec.color = s.color;
                        return true;
                    }
                }
                return false;
            }

            bool hit(ray r, float tmin, float tmax, inout hitRecord rec, hitableList list)
            {
                hitRecord tempRec;
                bool hitAny = false;
                float closestSoFar = tmax;
                for (int i = 0; i < list.size; i++)
                {
                    if (hitSphere(r, tmin, closestSoFar, tempRec, list.sList[i]))
                    {
                        hitAny = true;
                        closestSoFar = tempRec.t;
                        rec = tempRec;
                    }
                }
                return hitAny;
            }

            ray getRay(float u, float v, camera cam)
            {
                ray r;
                r.A = cam.o;
                r.B = cam.llc + u * cam.h + v * cam.v;
                return r;
            }

            float random(float2 st)
            {
                float a = 12.9898;
                float b = 78.233;
                float c = 43758.5453;
                float dt = dot(st, float2(a, b));
                float sn = fmod(dt, 3.14);
                return frac(sin(sn) * c);
            }

            float3 randInUnitSphere(float2 st)
            {
                float phi = random(st.yx) * 2.0 * PI;
                float theta = random(st.xy) * 3.14169265;
                return float3(cos(phi) * sin(theta), cos(theta), sin(phi) * sin(theta));
            }

            float3 color(ray r, hitableList list, float2 st)
            {
                hitRecord rec;
                float3 unitDirection;
                float t;
                float3 att = float3(1.0, 1.0, 1.0);
                int bounceSize = 10;
                int bounce = 0;

                // Bounce until we hit nothing or run out of bounces.
                while (hit(r, 0.001, FLT_MAX, rec, list) && bounce < bounceSize)
                {
                    unitDirection = normalize(direction(r));
                    if (rec.mat == 0)
                    {
                        float3 target = rec.p + rec.normal + randInUnitSphere(st);
                        r.A = rec.p;
                        r.B = target - rec.p;
                        att *= rec.color;
                    }
                    else if (rec.mat == 1)
                    {
                        float3 reflected = reflect(normalize(direction(r)), rec.normal);
                        r.A = rec.p;
                        r.B = reflected;
                        att *= rec.color;
                    }
                    else if (rec.mat == 2)
                    {
                        float refractiveIndex = 1.5;
                        float3 refracted = refract(unitDirection, rec.normal, 1.0 / refractiveIndex);
                        r.A = rec.p;
                        r.B = refracted;
                    }
                    bounce++;
                }
                unitDirection = normalize(direction(r));
                t = (unitDirection.y + 1.0);
                // Sample _MainTex using the xy components of unitDirection wrapped into [0,1]
                float3 texColor = tex2D(_MainTex, frac(unitDirection.xy)).xyz;
                return att * (t * float3(0.6, 0.8, 1.0) * texColor);
            }

            float4 frag(v2f i) : SV_Target
            {
                // Compute fragment coordinates from UV.
                float2 fragCoord = i.uv * _Resolution.xy;
                float2 st = fragCoord / _Resolution.xy;

                // Multiply _Time.x to speed up the animation.
                float fastTime = _Time.x * 4.0;

                // Setup camera parameters.
                camera cam;
                cam.llc = float3(-2.0, -1.0, -1.0);
                cam.h   = float3(4.0, 0.0, 0.0);
                cam.v   = float3(0.0, 2.25, 0.0);
                cam.o   = float3(0.0, 0.0, 0.0);

                // Setup hitable list and manually assign four spheres.
                hitableList list;
                list.size = 4;
                list.sList[0].center = float3(0.0, 0.0, -1.5);
                list.sList[0].radius = 0.5;
                list.sList[0].mat    = 0;
                list.sList[0].color  = float3(0.8, 0.3, 0.3);

                list.sList[1].center = float3(-1.0, 0.0, -1.5 + sin(fastTime));
                list.sList[1].radius = 0.5;
                list.sList[1].mat    = 1;
                list.sList[1].color  = float3(0.8, 0.8, 0.8);

                list.sList[2].center = float3(1.0, 0.0, -1.5 + cos(fastTime));
                list.sList[2].radius = 0.5;
                list.sList[2].mat    = 1;
                list.sList[2].color  = float3(0.8, 0.6, 0.2);

                list.sList[3].center = float3(0.0, -100.5, -1.0);
                list.sList[3].radius = 100.0;
                list.sList[3].mat    = 0;
                list.sList[3].color  = float3(0.8, 0.8, 0.0);

                // Generate primary ray from camera.
                ray r = getRay(st.x, st.y, cam);
                float3 col = float3(0.0, 0.0, 0.0);
                float sizeBlending = 20.0;
                // Accumulate color over several samples for blending.
                for (int x = 0; x < int(sizeBlending); x++)
                {
                    // Offset st by a function of x and fastTime for variation.
                    col += color(r, list, st + float2(x, x) + fastTime);
                }
                col /= sizeBlending;
                col = sqrt(col); // Gamma correction

                return float4(col, 1.0);
            }
            ENDCG
        }
    }
    FallBack "Diffuse"
}
