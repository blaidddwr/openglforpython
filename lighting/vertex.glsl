#version 430 core

in vec3 position;
in vec2 texturePoint;
in vec3 normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec2 fragmentTexturePoint;
out vec3 fragmentPosition;
out vec3 fragmentNormal;

void main()
{
    gl_Position = projection*view*model*vec4(position,1.0);
    fragmentTexturePoint = texturePoint;
    fragmentPosition = (model*vec4(position,1.0)).xyz;
    fragmentNormal = mat3(model)*normal;
}
