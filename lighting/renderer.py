from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FRAGMENT_SHADER
from OpenGL.GL import GL_LINEAR
from OpenGL.GL import GL_NEAREST
from OpenGL.GL import GL_REPEAT
from OpenGL.GL import GL_STATIC_DRAW
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import glClear
from OpenGL.GL import glEnable
from OpenGL.GL import glViewport
from PySide6.QtGui import QMatrix4x4
from PySide6.QtGui import QVector4D
from ctypes import Structure as cStructure
from ctypes import c_char
from ctypes import c_float
from opengl import Buffer
from opengl import Program
from opengl import Shader
from opengl import Texture2D
from opengl import VertexArray
import base


class PointLight(cStructure):

    _fields_ = [
        ("position",c_float*3)
        ,("p0",c_char*4)
        ,("color",c_float*3)
        ,("power",c_float)
    ]

    _pack_ = 1


class Renderer(base.Renderer):

    def __init__(self):
        super().__init__()
        self.__model = None
        self.__view = None
        self.__projection = None
        self.__angle = 0.0
        self.__theta = 0.0
        self.__phi = 0.0
        self.__lights = (PointLight*3)()
        self.__lights[0].position = (2,2,5)
        self.__lights[0].color = (1,0,0)
        self.__lights[0].power = 5
        self.__lights[1].position = (-4,-4,0)
        self.__lights[1].color = (0,0,1)
        self.__lights[1].power = 7
        self.__lights[2].position = (2,2,-5)
        self.__lights[2].color = (0,1,0)
        self.__lights[2].power = 6

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
        del self.__texture
        del self.__vao
        del self.__program
        del self.__lightsUBO

    def _init(self):
        self.__initProgram()
        self.__initVertices()
        self.__initTexture()
        self.__initTransform()
        self.__initLight()

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
                if self.__view is None:
                    self.__view = QMatrix4x4()
                    self.__view.translate(0,0,-3)
                    self.__view.rotate(self.__phi,-1,0,0)
                    self.__view.rotate(self.__theta,0,0,-1)
                    self.__viewUniform.setMatrix4f(self.__view)
                    (ivm,invertible) = self.__view.inverted()
                    if not invertible:
                        raise RuntimeError
                    cp = ivm.map(QVector4D(0,0,0,1))
                    self.__cameraPositionUniform.set3f(cp.x(),cp.y(),cp.z())
                if self.__model is None:
                    self.__model = QMatrix4x4()
                    self.__model.rotate(self.__angle,0,0,1)
                    self.__modelUniform.setMatrix4f(self.__model)
                self.__texture.bind(0)
                self.__lightsUBO.bindToUniform(0)
                vao.draw()
        glClear(GL_DEPTH_BUFFER_BIT)

    def __initLight(self):
        self.__lightsUBO = Buffer.fromData(self.__lights,GL_STATIC_DRAW)
        with self.__program as program:
            self.__cameraPositionUniform = program.uniform.cameraPosition
            program.ubo.lightBlock.setBlockBinding(0)

    def __initProgram(self):
        self.__program = Program(
            Shader(self._shader("vertex.glsl"),GL_VERTEX_SHADER)
            ,Shader(self._shader("fragment.glsl"),GL_FRAGMENT_SHADER)
            )

    def __initTexture(self):
        img = self._image("wood.jpeg")
        self.__texture = Texture2D(1,img.width(),img.height())
        self.__texture.load(img)
        self.__texture.setWrapS(GL_REPEAT)
        self.__texture.setWrapT(GL_REPEAT)
        self.__texture.setMinifyFilter(GL_NEAREST)
        self.__texture.setMagnifyFilter(GL_LINEAR)
        with self.__program as program:
            program.uniform.imageTexture.set1i(0)

    def __initTransform(self):
        with self.__program as program:
            self.__modelUniform = program.uniform.model
            self.__viewUniform = program.uniform.view
            self.__projectionUniform = program.uniform.projection

    def __initVertices(self):
        vertices = (
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
        with self.__program as program:
            self.__vao = VertexArray(
                GL_TRIANGLES
                ,(
                    (program.position,GL_FLOAT,3,0)
                    ,(program.texturePoint,GL_FLOAT,2,12)
                    ,(program.normal,GL_FLOAT,3,20)
                    )
                )
            self.__vao.createWithFloats(vertices)
