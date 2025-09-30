from OpenGL.GL import GL_ARRAY_BUFFER
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FRAGMENT_SHADER
from OpenGL.GL import GL_STATIC_DRAW
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import glClear
from OpenGL.GL import glViewport
from opengl import Buffer
from opengl import Program
from opengl import Shader
from opengl import VertexArray
import base


class Item(base.Item):

    def _createRenderer(self) -> base.Renderer:
        return Renderer()


class Renderer(base.Renderer):

    def _destroy(self):
        del self.__instanceBuffer
        del self.__vao
        del self.__program

    def _init(self):
        self.__initProgram()
        self.__initVertices()

    def _paint(self):
        glViewport(0,0,self.viewportSize().width(),self.viewportSize().height())
        with self.__program:
            with self.__vao as vao:
                vao.drawInstanced()
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
        instance = (
            -0.5,-0.5,0.5
            ,0.5,-0.5,0.5
            ,0,0.5,0.5
            ,0,-0.15,0.5
        )
        with self.__program as program:
            self.__vao = VertexArray.fromFloats(
                vertices
                ,GL_TRIANGLES
                ,(
                    (program.position,3,GL_FLOAT,24,0)
                    ,(program.color,3,GL_FLOAT,24,12)
                    )
                ,len(instance)//3
                )
            with self.__vao as vao:
                self.__instanceBuffer = Buffer.fromFloats(instance,GL_STATIC_DRAW)
                self.__instanceBuffer.bind(GL_ARRAY_BUFFER)
                vao.add(program.offset,2,GL_FLOAT,12,0,1)
                vao.add(program.scale,1,GL_FLOAT,12,8,1)


_vertexShaderSrc = """#version 450 core

in vec3 position;
in vec3 color;
in vec2 offset;
in float scale;

out vec3 fColor;

void main()
{

    gl_Position = vec4(vec3((scale*position.xy)+offset,position.z),1.0);
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
