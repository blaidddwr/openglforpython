from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FRAGMENT_SHADER
from OpenGL.GL import GL_LINEAR
from OpenGL.GL import GL_NEAREST
from OpenGL.GL import GL_REPEAT
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import glClear
from OpenGL.GL import glViewport
from opengl import Program
from opengl import Shader
from opengl import Texture2DArray
from opengl import VertexArray
import base


class Item(base.Item):

    def _createRenderer(self) -> base.Renderer:
        return Renderer()


class Renderer(base.Renderer):

    def _init(self):
        self.__initProgram()
        self.__initVertices()
        self.__initTexture()

    def _paint(self):
        glViewport(0,0,self.viewportSize().width(),self.viewportSize().height())
        with self.__program:
            with self.__vao as vao:
                self.__texture.bind(0)
                vao.draw()
        glClear(GL_DEPTH_BUFFER_BIT)

    def _destroy(self):
        del self.__texture
        del self.__vao
        del self.__program

    def __initProgram(self):
        self.__program = Program(
            Shader(_vertexShaderSrc,GL_VERTEX_SHADER)
            ,Shader(_fragmentShaderSrc,GL_FRAGMENT_SHADER)
            )

    def __initTexture(self):
        self.__texture = Texture2DArray.fromImages(
            1
            ,(
                self._image("wood.jpeg")
                ,self._image("metal.jpeg")
                ,self._image("grass.jpeg")
                )
            )
        self.__texture.setWrapS(GL_REPEAT)
        self.__texture.setWrapT(GL_REPEAT)
        self.__texture.setMinifyFilter(GL_NEAREST)
        self.__texture.setMagnifyFilter(GL_LINEAR)
        with self.__program as program:
            program.uniform.imageTexture.set1i(0)

    def __initVertices(self):
        vertices = (
            -0.5,-0.5,0.0,1.0,0.0,0.0,0.0,1.0,1,0,0
            ,0.5,-0.5,0.0,0.0,1.0,0.0,1.0,1.0,0,1,0
            ,0.0,0.5,0.0,0.0,0.0,1.0,0.5,0.0,0,0,1
        )
        with self.__program as program:
            self.__vao = VertexArray.fromFloats(
                vertices
                ,GL_TRIANGLES
                ,(
                    (program.position,3,GL_FLOAT,44,0)
                    ,(program.color,3,GL_FLOAT,44,12)
                    ,(program.texturePoint,2,GL_FLOAT,44,24)
                    ,(program.textureWeight,3,GL_FLOAT,44,32)
                    )
                )


_vertexShaderSrc = """#version 430 core

in vec3 position;
in vec3 color;
in vec2 texturePoint;
in vec3 textureWeight;

out vec3 fColor;
out vec2 fTexturePoint;
out vec3 fTextureWeight;

void main()
{
    gl_Position = vec4(position,1.0);
    fColor = color;
    fTexturePoint = texturePoint;
    fTextureWeight = textureWeight;
}
"""

_fragmentShaderSrc = """#version 430 core

in vec3 fColor;
in vec2 fTexturePoint;
in vec3 fTextureWeight;

uniform sampler2DArray imageTexture;

out vec4 color;

void main()
{
    vec4 color0 = texture(imageTexture,vec3(fTexturePoint,0));
    vec4 color1 = texture(imageTexture,vec3(fTexturePoint,1));
    vec4 color2 = texture(imageTexture,vec3(fTexturePoint,2));
    float den = fTextureWeight.x+fTextureWeight.y+fTextureWeight.z;
    color = (
        (color0*fTextureWeight.x/den)
        +(color1*fTextureWeight.y/den)
        +(color2*fTextureWeight.z/den)
        );
}
"""
