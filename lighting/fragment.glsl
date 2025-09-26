#version 430 core
#define LIGHT_SIZE 3

struct Light
{
    vec3 position;
    vec3 color;
    float power;
};

in vec2 fragmentTexturePoint;
in vec3 fragmentPosition;
in vec3 fragmentNormal;

uniform sampler2D imageTexture;
uniform vec3 cameraPosition;
layout (std140) uniform lightBlock
{
    Light lights[LIGHT_SIZE];
};

out vec4 color;

vec3 calcPointLight(Light light,vec3 fPos,vec3 fNorm,vec3 textureColor)
{
    vec3 ret = vec3(0.0);
    vec3 ftl = light.position-fPos;
    float d = length(ftl);
    ftl = normalize(ftl);
    vec3 ftc = normalize(cameraPosition-fPos);
    vec3 hw = normalize(ftl+ftc);
    ret += textureColor*light.color*light.power*max(0.0,dot(fNorm,ftl))/pow(d,2);
    ret += light.color*light.power*pow(max(0.0,dot(fNorm,hw)),32)/pow(d,2);
    return ret;
}

void main()
{
    vec3 tc = texture(imageTexture,fragmentTexturePoint).xyz;
    vec3 ret = 0.2*tc.xyz;
    for (int i = 0;i < LIGHT_SIZE;i++)
    {
        ret += calcPointLight(lights[i],fragmentPosition,fragmentNormal,tc);
    }
    color = vec4(ret,1.0);
}
