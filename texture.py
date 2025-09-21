from OpenGL.GL import GL_ARRAY_BUFFER
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FRAGMENT_SHADER
from OpenGL.GL import GL_LINEAR
from OpenGL.GL import GL_NEAREST
from OpenGL.GL import GL_REPEAT
from OpenGL.GL import GL_RGBA
from OpenGL.GL import GL_STATIC_DRAW
from OpenGL.GL import GL_TEXTURE0
from OpenGL.GL import GL_TEXTURE_2D
from OpenGL.GL import GL_TEXTURE_MAG_FILTER
from OpenGL.GL import GL_TEXTURE_MIN_FILTER
from OpenGL.GL import GL_TEXTURE_WRAP_S
from OpenGL.GL import GL_TEXTURE_WRAP_T
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import glActiveTexture
from OpenGL.GL import glBindBuffer
from OpenGL.GL import glBindTexture
from OpenGL.GL import glBindVertexArray
from OpenGL.GL import glBufferData
from OpenGL.GL import glClear
from OpenGL.GL import glDeleteBuffers
from OpenGL.GL import glDeleteProgram
from OpenGL.GL import glDeleteTextures
from OpenGL.GL import glDeleteVertexArrays
from OpenGL.GL import glDrawArrays
from OpenGL.GL import glEnableVertexAttribArray
from OpenGL.GL import glGenBuffers
from OpenGL.GL import glGenTextures
from OpenGL.GL import glGenVertexArrays
from OpenGL.GL import glGenerateMipmap
from OpenGL.GL import glGetUniformLocation
from OpenGL.GL import glTexImage2D
from OpenGL.GL import glTexParameteri
from OpenGL.GL import glUniform1i
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

    def _init(self):
        self.__initProgram()
        self.__initVertices()
        self.__initTexture()

    def _paint(self):
        glViewport(0,0,self.viewportSize().width(),self.viewportSize().height())
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.__texture)
        glUseProgram(self.__program)
        glBindVertexArray(self.__vao)
        glDrawArrays(GL_TRIANGLES,0,self.__vertexSize)
        glClear(GL_DEPTH_BUFFER_BIT)

    def _destroy(self):
        glDeleteTextures(1,(self.__texture,))
        glDeleteBuffers(1,(self.__vbo,))
        glDeleteVertexArrays(1,(self.__vao,))
        glDeleteProgram(self.__program)

    def __initProgram(self):
        self.__program = compileProgram(
            compileShader(_vertexShaderSrc,GL_VERTEX_SHADER)
            ,compileShader(_fragmentShaderSrc,GL_FRAGMENT_SHADER)
            )
        glUseProgram(self.__program)

    def __initTexture(self):
        glUniform1i(glGetUniformLocation(self.__program,"imageTexture"),0)
        img = self._texture("wood.jpeg")
        self.__texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.__texture)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexImage2D(
            GL_TEXTURE_2D
            ,0
            ,GL_RGBA
            ,img.width()
            ,img.height()
            ,0
            ,GL_RGBA
            ,GL_UNSIGNED_BYTE
            ,img.bits()
            )
        glGenerateMipmap(GL_TEXTURE_2D)

    def __initVertices(self):
        self.__vertices = (
            -0.5,-0.5,0.0,1.0,0.0,0.0,0.0,1.0
            ,0.5,-0.5,0.0,0.0,1.0,0.0,1.0,1.0
            ,0.0,0.5,0.0,0.0,0.0,1.0,0.5,0.0
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
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2,2,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(24))


_vertexShaderSrc = """
#version 430 core

layout (location=0) in vec3 vertexPos;
layout (location=1) in vec3 vertexColor;
layout (location=2) in vec2 vertexTexCoord;

out vec3 fragmentColor;
out vec2 fragmentTexCoord;

void main()
{
    gl_Position = vec4(vertexPos,1.0);
    fragmentColor = vertexColor;
    fragmentTexCoord = vertexTexCoord;
}
"""

_fragmentShaderSrc = """
#version 430 core

in vec3 fragmentColor;
in vec2 fragmentTexCoord;

uniform sampler2D imageTexture;

out vec4 color;

void main()
{
    color = vec4(fragmentColor,1.0)*texture(imageTexture,fragmentTexCoord);
}
"""
