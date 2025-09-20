from OpenGL.GL import GL_ARRAY_BUFFER
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FRAGMENT_SHADER
from OpenGL.GL import GL_STATIC_DRAW
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import glBindBuffer
from OpenGL.GL import glBindVertexArray
from OpenGL.GL import glBufferData
from OpenGL.GL import glClear
from OpenGL.GL import glDeleteBuffers
from OpenGL.GL import glDeleteProgram
from OpenGL.GL import glDeleteVertexArrays
from OpenGL.GL import glDrawArrays
from OpenGL.GL import glEnableVertexAttribArray
from OpenGL.GL import glGenBuffers
from OpenGL.GL import glGenVertexArrays
from OpenGL.GL import glUseProgram
from OpenGL.GL import glVertexAttribPointer
from OpenGL.GL import glViewport
from OpenGL.GL.shaders import compileProgram
from OpenGL.GL.shaders import compileShader
import base
import ctypes
import numpy as np


class Item(base.Item):

    def _createRenderer(self) -> base.Renderer:
        return Renderer()


class Renderer(base.Renderer):

    def _destroy(self):
        glDeleteBuffers(1,(self.__vbo,))
        glDeleteVertexArrays(1,(self.__vao,))
        glDeleteProgram(self.__program)

    def _init(self):
        self.__initProgram()
        self.__initVertices()
        self.__init = True

    def _paint(self):
        glViewport(0,0,self.viewportSize().width(),self.viewportSize().height())
        glUseProgram(self.__program)
        glBindVertexArray(self.__vao)
        glDrawArrays(GL_TRIANGLES,0,self.__vertexSize)
        glClear(GL_DEPTH_BUFFER_BIT)

    def __initProgram(self):
        self.__program = compileProgram(
            compileShader(_vertexShaderSrc,GL_VERTEX_SHADER)
            ,compileShader(_fragmentShaderSrc,GL_FRAGMENT_SHADER)
            )
        glUseProgram(self.__program)

    def __initVertices(self):
        self.__vertices = (
            -0.5,-0.5,0.0,1.0,0.0,0.0
            ,0.5,-0.5,0.0,0.0,1.0,0.0
            ,0.0,0.5,0.0,0.0,0.0,1.0
        )
        self.__vertices = np.array(self.__vertices,dtype=np.float32)
        self.__vertexSize = 3
        self.__vao = glGenVertexArrays(1)
        glBindVertexArray(self.__vao)
        self.__vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,self.__vbo)
        glBufferData(
            GL_ARRAY_BUFFER
            ,self.__vertices.nbytes
            ,self.__vertices
            ,GL_STATIC_DRAW
            )
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,24,ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,24,ctypes.c_void_p(12))


_vertexShaderSrc = """
#version 430 core

layout (location=0) in vec3 position;
layout (location=1) in vec3 color;

out vec3 fColor;

void main()
{
    gl_Position = vec4(position,1.0);
    fColor = color;
}
"""

_fragmentShaderSrc = """
#version 430 core

in vec3 fColor;

out vec4 color;

void main()
{
    color = vec4(fColor,1.0);
}
"""
