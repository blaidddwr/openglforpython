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
from OpenGL.GL import glUniform1f
from OpenGL.GL import glUniform1i
from OpenGL.GL import glUniform3fv
from OpenGL.GL import glUniformMatrix4fv
from OpenGL.GL import glUseProgram
from OpenGL.GL import glVertexAttribPointer
from OpenGL.GL import glViewport
from OpenGL.GL.shaders import compileProgram
from PySide6.QtGui import QMatrix4x4
from PySide6.QtGui import QVector4D
import base
import ctypes
import numpy as np


class Renderer(base.Renderer):

    def __init__(self):
        super().__init__()
        self.__model = None
        self.__view = None
        self.__projection = None
        self.__angle = 0.0
        self.__theta = 0.0
        self.__phi = 0.0
        self.__cameraPosition = (0,0,0)
        self.__lights = (
            ((2,2,5),(1,0,0),5)
            ,((-4,-4,0),(0,0,1),7)
            ,((2,2,-5),(0,1,0),6)
        )

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
        self.__initLight()
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
            (ivm,invertible) = self.__view.inverted()
            if not invertible:
                raise RuntimeError
            cp = ivm.map(QVector4D(0,0,0,1))
            self.__cameraPosition = (cp.x(),cp.y(),cp.z())
        if self.__model is None:
            self.__model = QMatrix4x4()
            self.__model.rotate(self.__angle,0,0,1)
        glViewport(0,0,self.viewportSize().width(),self.viewportSize().height())
        glEnable(GL_DEPTH_TEST)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.__texture)
        glUseProgram(self.__program)
        glBindVertexArray(self.__vao)
        for (i,light) in enumerate(self.__lights):
            glUniform3fv(self.__lightLocations[i]["position"],1,light[0])
            glUniform3fv(self.__lightLocations[i]["color"],1,light[1])
            glUniform1f(self.__lightLocations[i]["power"],light[2])
        glUniform3fv(self.__cameraPositionLocation,1,self.__cameraPosition)
        glUniformMatrix4fv(self.__modelLocation,1,GL_FALSE,self.__model.data())
        glUniformMatrix4fv(self.__viewLocation,1,GL_FALSE,self.__view.data())
        glUniformMatrix4fv(self.__projectionLocation,1,GL_FALSE,self.__projection.data())
        glDrawArrays(GL_TRIANGLES,0,self.__vertexSize)
        glClear(GL_DEPTH_BUFFER_BIT)

    def __initLight(self):
        self.__cameraPositionLocation = glGetUniformLocation(self.__program,"cameraPosition")
        self.__lightLocations = [
            {
                "position": glGetUniformLocation(self.__program,f"pointLights[{i}].position")
                ,"color": glGetUniformLocation(self.__program,f"pointLights[{i}].color")
                ,"power": glGetUniformLocation(self.__program,f"pointLights[{i}].power")
            }
            for i in range(len(self.__lights))
        ]

    def __initProgram(self):
        self.__program = compileProgram(
            self._compileShader("vertex.glsl",GL_VERTEX_SHADER)
            ,self._compileShader("fragment.glsl",GL_FRAGMENT_SHADER)
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
            -0.5,-0.5,-0.5,0,0,0,0,-1
            ,0.5,-0.5,-0.5,1,0,0,0,-1
            ,0.5,0.5,-0.5,1,1,0,0,-1
            ,0.5,0.5,-0.5,1,1,0,0,-1
            ,-0.5,0.5,-0.5,0,1,0,0,-1
            ,-0.5,-0.5,-0.5,0,0,0,0,-1
            ,-0.5,-0.5,0.5,0,0,0,0,1
            ,0.5,-0.5,0.5,1,0,0,0,1
            ,0.5,0.5,0.5,1,1,0,0,1
            ,0.5,0.5,0.5,1,1,0,0,1
            ,-0.5,0.5,0.5,0,1,0,0,1
            ,-0.5,-0.5,0.5,0,0,0,0,1
            ,-0.5,0.5,0.5,1,0,-1,0,0
            ,-0.5,0.5,-0.5,1,1,-1,0,0
            ,-0.5,-0.5,-0.5,0,1,-1,0,0
            ,-0.5,-0.5,-0.5,0,1,-1,0,0
            ,-0.5,-0.5,0.5,0,0,-1,0,0
            ,-0.5,0.5,0.5,1,0,-1,0,0
            ,0.5,0.5,0.5,1,0,1,0,0
            ,0.5,0.5,-0.5,1,1,1,0,0
            ,0.5,-0.5,-0.5,0,1,1,0,0
            ,0.5,-0.5,-0.5,0,1,1,0,0
            ,0.5,-0.5,0.5,0,0,1,0,0
            ,0.5,0.5,0.5,1,0,1,0,0
            ,-0.5,-0.5,-0.5,0,1,0,-1,0
            ,0.5,-0.5,-0.5,1,1,0,-1,0
            ,0.5,-0.5,0.5,1,0,0,-1,0
            ,0.5,-0.5,0.5,1,0,0,-1,0
            ,-0.5,-0.5,0.5,0,0,0,-1,0
            ,-0.5,-0.5,-0.5,0,1,0,-1,0
            ,-0.5,0.5,-0.5,0,1,0,1,0
            ,0.5,0.5,-0.5,1,1,0,1,0
            ,0.5,0.5,0.5,1,0,0,1,0
            ,0.5,0.5,0.5,1,0,0,1,0
            ,-0.5,0.5,0.5,0,0,0,1,0
            ,-0.5,0.5,-0.5,0,1,0,1,0
        )
        self.__vertexSize = len(self.__vertices)//8
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
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,2,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2,3,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(20))

    def __updateProjection(self):
        self.__projection = QMatrix4x4()
        self.__projection.perspective(45,self._window.width()/self._window.height(),0.1,10)
