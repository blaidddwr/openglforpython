from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FRAGMENT_SHADER
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import glClear
from OpenGL.GL import glViewport
from opengl import VertexArray
from opengl import Program
from opengl import Shader
import base


class Item(base.Item):

    def _createRenderer(self) -> base.Renderer:
        return Renderer()


class Renderer(base.Renderer):

    def _destroy(self):
        del self.__vao
        del self.__program

    def _init(self):
        self.__initProgram()
        self.__initVertices()

    def _paint(self):
        glViewport(0,0,self.viewportSize().width(),self.viewportSize().height())
        with self.__program:
            with self.__vao as vao:
                vao.draw()
        glClear(GL_DEPTH_BUFFER_BIT)

    def __initProgram(self):
        self.__program = Program(
            Shader(_vertexShaderSrc,GL_VERTEX_SHADER)
            ,Shader(_fragmentShaderSrc,GL_FRAGMENT_SHADER)
            )

    def __initVertices(self):
        vertices = (
            -0.5,-0.5,0.0,1.0,0.0,0.0
            ,0.5,-0.5,0.0,0.0,1.0,0.0
            ,0.0,0.5,0.0,0.0,0.0,1.0
        )
        with self.__program as program:
            self.__vao = VertexArray(
                GL_TRIANGLES
                ,(
                    (program.position,GL_FLOAT,3,0)
                    ,(program.color,GL_FLOAT,3,12)
                    )
                )
            self.__vao.createWithFloats(vertices)


_vertexShaderSrc = """#version 450 core

in vec3 position;
in vec3 color;

out vec3 fColor;

void main()
{
    gl_Position = vec4(position,1.0);
    fColor = color;
}
"""

_fragmentShaderSrc = """#version 450 core

in vec3 fColor;

out vec4 color;

void main()
{
    color = vec4(fColor,1.0);
}
"""
