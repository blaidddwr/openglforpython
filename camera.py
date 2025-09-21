from OpenGL.GL import GL_ARRAY_BUFFER
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_DEPTH_TEST
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
from OpenGL.GL import glEnable
from OpenGL.GL import glEnableVertexAttribArray
from OpenGL.GL import glGenBuffers
from OpenGL.GL import glGenTextures
from OpenGL.GL import glGenVertexArrays
from OpenGL.GL import glGenerateMipmap
from OpenGL.GL import glGetUniformLocation
from OpenGL.GL import glTexImage2D
from OpenGL.GL import glTexParameteri
from OpenGL.GL import glUniform1i
from OpenGL.GL import glUniformMatrix4fv
from OpenGL.GL import glUseProgram
from OpenGL.GL import glVertexAttribPointer
from OpenGL.GL import glViewport
from OpenGL.GL.shaders import compileProgram
from OpenGL.GL.shaders import compileShader
from PySide6.QtCore import QObject
from PySide6.QtCore import QTimerEvent
from PySide6.QtCore import Qt
from PySide6.QtGui import QMatrix4x4
from PySide6.QtGui import QMouseEvent
import base
import ctypes
import numpy as np


class Item(base.Item):

    def __init__(self,parent:QObject = None):
        super().__init__(parent)
        self.startTimer(16)
        self.__cubeSpinning = False
        self.__angle = 0
        self.__theta = 0
        self.__phi = 0
        self.setAcceptedMouseButtons(Qt.LeftButton)

    def mouseDoubleClickEvent(self,event:QMouseEvent) -> None:
        self.__cubeSpinning = not self.__cubeSpinning
        event.accept()

    def mouseMoveEvent(self,event:QMouseEvent) -> None:
        dx = self.__mouseStartX-event.globalPosition().x()
        dy = self.__mouseStartY-event.globalPosition().y()
        dx = dx/self.window().width()
        dy = dy/self.window().height()
        self.__theta = self.__thetaStart+dx*360
        if self.__theta < 0:
            self.__theta += 360
        elif self.__theta >= 360:
            self.__theta -= 360
        self.__phi = max(0,min(180,self.__phiStart+dy*360))
        self.window().update()
        event.accept()

    def mousePressEvent(self,event:QMouseEvent) -> None:
        self.__mouseStartX = event.globalPosition().x()
        self.__mouseStartY = event.globalPosition().y()
        self.__thetaStart = self.__theta
        self.__phiStart = self.__phi
        event.accept()

    def timerEvent(self,event:QTimerEvent) -> None:
        if self.__cubeSpinning:
            self.__angle += 0.5
            self.window().update()

    def _createRenderer(self) -> base.Renderer:
        return Renderer()

    def _sync(self,renderer:base.Renderer) -> None:
        renderer.setAngle(self.__angle)
        renderer.setTheta(self.__theta)
        renderer.setPhi(self.__phi)


class Renderer(base.Renderer):

    def __init__(self):
        super().__init__()
        self.__model = None
        self.__view = None
        self.__projection = None
        self.__angle = 0.0
        self.__theta = 0.0
        self.__phi = 0.0

    def setAngle(self,value:float) -> None:
        self.__angle = value
        self.__model = None

    def setPhi(self,value:float) -> None:
        self.__phi = value
        self.__view = None

    def setTheta(self,value:float) -> None:
        self.__theta = value
        self.__view = None

    def _destroy(self):
        glDeleteTextures(1,(self.__texture,))
        glDeleteBuffers(1,(self.__vbo,))
        glDeleteVertexArrays(1,(self.__vao,))
        glDeleteProgram(self.__program)

    def _init(self):
        self.__initProgram()
        self.__initVertices()
        self.__initTexture()
        self.__initTransform()
        self.__init = True

    def _resize(self):
        self.__projection = None

    def _paint(self):
        if self.__projection is None:
            self.__projection = QMatrix4x4()
            aspectRatio = self.viewportSize().width()/self.viewportSize().height()
            self.__projection.perspective(45,aspectRatio,0.1,10)
        if self.__view is None:
            self.__view = QMatrix4x4()
            self.__view.translate(0,0,-3)
            self.__view.rotate(self.__phi,-1,0,0)
            self.__view.rotate(self.__theta,0,0,-1)
        if self.__model is None:
            self.__model = QMatrix4x4()
            self.__model.rotate(self.__angle,0,0,1)
        glViewport(0,0,self.viewportSize().width(),self.viewportSize().height())
        glEnable(GL_DEPTH_TEST)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.__texture)
        glUseProgram(self.__program)
        glBindVertexArray(self.__vao)
        glUniformMatrix4fv(self.__modelLocation,1,GL_FALSE,self.__model.data())
        glUniformMatrix4fv(self.__viewLocation,1,GL_FALSE,self.__view.data())
        glUniformMatrix4fv(self.__projectionLocation,1,GL_FALSE,self.__projection.data())
        glDrawArrays(GL_TRIANGLES,0,self.__vertexSize)
        glClear(GL_DEPTH_BUFFER_BIT)

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

    def __initTransform(self):
        self.__modelLocation = glGetUniformLocation(self.__program,"model")
        self.__viewLocation = glGetUniformLocation(self.__program,"view")
        self.__projectionLocation = glGetUniformLocation(self.__program,"projection")

    def __initVertices(self):
        self.__vertices = (
            -0.5,-0.5,-0.5,0,0
            ,0.5,-0.5,-0.5,1,0
            ,0.5,0.5,-0.5,1,1
            ,0.5,0.5,-0.5,1,1
            ,-0.5,0.5,-0.5,0,1
            ,-0.5,-0.5,-0.5,0,0
            ,-0.5,-0.5,0.5,0,0
            ,0.5,-0.5,0.5,1,0
            ,0.5,0.5,0.5,1,1
            ,0.5,0.5,0.5,1,1
            ,-0.5,0.5,0.5,0,1
            ,-0.5,-0.5,0.5,0,0
            ,-0.5,0.5,0.5,1,0
            ,-0.5,0.5,-0.5,1,1
            ,-0.5,-0.5,-0.5,0,1
            ,-0.5,-0.5,-0.5,0,1
            ,-0.5,-0.5,0.5,0,0
            ,-0.5,0.5,0.5,1,0
            ,0.5,0.5,0.5,1,0
            ,0.5,0.5,-0.5,1,1
            ,0.5,-0.5,-0.5,0,1
            ,0.5,-0.5,-0.5,0,1
            ,0.5,-0.5,0.5,0,0
            ,0.5,0.5,0.5,1,0
            ,-0.5,-0.5,-0.5,0,1
            ,0.5,-0.5,-0.5,1,1
            ,0.5,-0.5,0.5,1,0
            ,0.5,-0.5,0.5,1,0
            ,-0.5,-0.5,0.5,0,0
            ,-0.5,-0.5,-0.5,0,1
            ,-0.5,0.5,-0.5,0,1
            ,0.5,0.5,-0.5,1,1
            ,0.5,0.5,0.5,1,0
            ,0.5,0.5,0.5,1,0
            ,-0.5,0.5,0.5,0,0
            ,-0.5,0.5,-0.5,0,1
        )
        self.__vertexSize = len(self.__vertices)//5
        self.__vertices = np.array(self.__vertices,dtype=np.float32)
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
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,20,ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,2,GL_FLOAT,GL_FALSE,20,ctypes.c_void_p(12))

    def __updateProjection(self):
        self.__projection = QMatrix4x4()
        self.__projection.perspective(45,self._window.width()/self._window.height(),0.1,10)


_vertexShaderSrc = """
#version 430 core

layout (location=0) in vec3 vertexPos;
layout (location=1) in vec2 vertexTexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec2 fragmentTexCoord;

void main()
{
    gl_Position = projection*view*model*vec4(vertexPos,1.0);
    fragmentTexCoord = vertexTexCoord;
}
"""

_fragmentShaderSrc = """
#version 430 core

in vec2 fragmentTexCoord;

uniform sampler2D imageTexture;

out vec4 color;

void main()
{
    color = texture(imageTexture,fragmentTexCoord);
}
"""
