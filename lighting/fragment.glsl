#version 430 core
#define LIGHT_SIZE 3

struct PointLight
{
    vec3 position;
    vec3 color;
    float power;
};

in vec2 fragmentTexCoord;
in vec3 fragmentPosition;
in vec3 fragmentNormal;

uniform sampler2D imageTexture;
uniform PointLight pointLights[LIGHT_SIZE];
uniform vec3 cameraPosition;

out vec4 color;

vec3 calcPointLight(PointLight light,vec3 fPos,vec3 fNorm,vec3 tColor)
{
    vec3 ret = vec3(0.0);
    vec3 ftl = light.position-fPos;
    float d = length(ftl);
    ftl = normalize(ftl);
    vec3 ftc = normalize(cameraPosition-fPos);
    vec3 hw = normalize(ftl+ftc);
    ret += tColor*light.color*light.power*max(0.0,dot(fNorm,ftl))/pow(d,2);
    ret += light.color*light.power*pow(max(0.0,dot(fNorm,hw)),32)/pow(d,2);
    return ret;
}

void main()
{
    vec3 tColor = texture(imageTexture,fragmentTexCoord).xyz;
    vec3 ret = 0.2*tColor.xyz;
    for (int i = 0;i < LIGHT_SIZE;i++)
    {
        ret += calcPointLight(pointLights[i],fragmentPosition,fragmentNormal,tColor);
    }
    color = vec4(ret,1.0);
}
