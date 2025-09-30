from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FRAGMENT_SHADER
from OpenGL.GL import GL_LINEAR
from OpenGL.GL import GL_NEAREST
from OpenGL.GL import GL_REPEAT
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import glClear
from OpenGL.GL import glEnable
from OpenGL.GL import glViewport
from PySide6.QtCore import QObject
from PySide6.QtCore import QTimerEvent
from PySide6.QtGui import QMatrix4x4
from opengl import Program
from opengl import Shader
from opengl import Texture2D
from opengl import VertexArray
import base


class Item(base.Item):

    def __init__(self,parent:QObject = None):
        super().__init__(parent)
        self.startTimer(16)
        self.__angle = 0

    def timerEvent(self,event:QTimerEvent) -> None:
        self.__angle += 0.5
        if self.window():
            self.window().update()

    def _createRenderer(self) -> base.Renderer:
        return Renderer()

    def _sync(self,renderer:base.Renderer) -> None:
        renderer.setAngle(self.__angle)


class Renderer(base.Renderer):

    def __init__(self):
        super().__init__()
        self.__model = None
        self.__projection = None
        self.__angle = 0.0

    def setAngle(self,angle:float) -> None:
        self.__angle = angle
        self.__model = None

    def _destroy(self):
        del self.__texture
        del self.__vao
        del self.__program

    def _init(self):
        self.__initProgram()
        self.__initVertices()
        self.__initTexture()
        self.__initTransform()

    def _resize(self):
        self.__projection = None

    def _paint(self):
        glViewport(0,0,self.viewportSize().width(),self.viewportSize().height())
        glEnable(GL_DEPTH_TEST)
        with self.__program:
            with self.__vao as vao:
                if self.__projection is None:
                    self.__projection = QMatrix4x4()
                    aspectRatio = self.viewportSize().width()/self.viewportSize().height()
                    self.__projection.perspective(45,aspectRatio,0.1,10)
                    self.__projectionUniform.setMatrix4f(self.__projection)
                if self.__model is None:
                    self.__model = QMatrix4x4()
                    self.__model.translate(0,0,-3)
                    self.__model.rotate(self.__angle,0,-1,0)
                    self.__modelUniform.setMatrix4f(self.__model)
                self.__texture.bind(0)
                vao.draw()
        glClear(GL_DEPTH_BUFFER_BIT)

    def __initProgram(self):
        self.__program = Program(
            Shader(_vertexShaderSrc,GL_VERTEX_SHADER)
            ,Shader(_fragmentShaderSrc,GL_FRAGMENT_SHADER)
            )

    def __initTexture(self):
        self.__texture = Texture2D.fromImage(1,self._image("wood.jpeg"))
        self.__texture.setWrapS(GL_REPEAT)
        self.__texture.setWrapT(GL_REPEAT)
        self.__texture.setMinifyFilter(GL_NEAREST)
        self.__texture.setMagnifyFilter(GL_LINEAR)
        with self.__program as program:
            program.uniform.imageTexture.set1i(0)

    def __initTransform(self):
        with self.__program as program:
            self.__modelUniform = program.uniform.model
            self.__projectionUniform = program.uniform.projection

    def __initVertices(self):
        vertices = (
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
        with self.__program as program:
            self.__vao = VertexArray.fromFloats(
                vertices
                ,GL_TRIANGLES
                ,(
                    (program.position,3,GL_FLOAT,20,0)
                    ,(program.texturePoint,2,GL_FLOAT,20,12)
                    )
                )


_vertexShaderSrc = """#version 430 core

in vec3 position;
in vec2 texturePoint;

uniform mat4 model;
uniform mat4 projection;

out vec2 fTexturePoint;

void main()
{
    gl_Position = projection*model*vec4(position,1.0);
    fTexturePoint = texturePoint;
}
"""

_fragmentShaderSrc = """#version 430 core

in vec2 fTexturePoint;

uniform sampler2D imageTexture;

out vec4 color;

void main()
{
    color = texture(imageTexture,fTexturePoint);
}
"""
