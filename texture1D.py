from OpenGL.GL import GL_CLAMP_TO_EDGE
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FRAGMENT_SHADER
from OpenGL.GL import GL_LINEAR
from OpenGL.GL import GL_NEAREST
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import glClear
from OpenGL.GL import glViewport
from opengl import Program
from opengl import Shader
from opengl import Texture1D
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
        colors = (
            90,76,66,255
            ,105,102,92,255
            ,97,90,74,255
            ,116,111,97,255
            ,170,170,170,255
        )
        self.__texture = Texture1D.fromArray(1,colors)
        self.__texture.setWrapS(GL_CLAMP_TO_EDGE)
        self.__texture.setMinifyFilter(GL_NEAREST)
        self.__texture.setMagnifyFilter(GL_LINEAR)
        with self.__program as program:
            program.uniform.imageTexture.set1i(0)

    def __initVertices(self):
        vertices = (
            -0.5,-0.5,0.0,0.0
            ,0.5,-0.5,0.0,1.0
            ,0.0,0.5,0.0,0.5
        )
        with self.__program as program:
            self.__vao = VertexArray.fromFloats(
                vertices
                ,GL_TRIANGLES
                ,(
                    (program.position,3,GL_FLOAT,16,0)
                    ,(program.texturePoint,1,GL_FLOAT,16,12)
                    )
                )


_vertexShaderSrc = """#version 430 core

in vec3 position;
in float texturePoint;

out float fTexturePoint;

void main()
{
    gl_Position = vec4(position,1.0);
    fTexturePoint = texturePoint;
}
"""

_fragmentShaderSrc = """#version 430 core

in float fTexturePoint;

uniform sampler1D imageTexture;

out vec4 color;

void main()
{
    color = texture(imageTexture,fTexturePoint);
}
"""
