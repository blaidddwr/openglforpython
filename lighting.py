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
from PySide6.QtCore import QObject
from PySide6.QtCore import QTimerEvent
from PySide6.QtCore import Qt
from PySide6.QtGui import QMatrix4x4
from PySide6.QtGui import QMouseEvent
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
            self.__vao = VertexArray.fromFloats(
                vertices
                ,GL_TRIANGLES
                ,(
                    (program.position,3,GL_FLOAT,32,0)
                    ,(program.texturePoint,2,GL_FLOAT,32,12)
                    ,(program.normal,3,GL_FLOAT,32,20)
                    )
                )


_vertexShaderSrc = """#version 430 core

in vec3 position;
in vec2 texturePoint;
in vec3 normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec2 fTexturePoint;
out vec3 fPosition;
out vec3 fNormal;

void main()
{
    gl_Position = projection*view*model*vec4(position,1.0);
    fTexturePoint = texturePoint;
    fPosition = (model*vec4(position,1.0)).xyz;
    fNormal = mat3(model)*normal;
}
"""

_fragmentShaderSrc = """#version 430 core
#define LIGHT_SIZE 3

struct Light
{
    vec3 position;
    vec3 color;
    float power;
};

in vec2 fTexturePoint;
in vec3 fPosition;
in vec3 fNormal;

uniform sampler2D imageTexture;
uniform vec3 cameraPosition;
layout (std140) uniform lightBlock
{
    Light lights[LIGHT_SIZE];
};

out vec4 color;

vec3 calcPointLight(Light light,vec3 fPos,vec3 fNorm,vec3 textureColor)
{
    vec3 ret = vec3(0.0);
    vec3 ftl = light.position-fPos;
    float d = length(ftl);
    ftl = normalize(ftl);
    vec3 ftc = normalize(cameraPosition-fPos);
    vec3 hw = normalize(ftl+ftc);
    ret += textureColor*light.color*light.power*max(0.0,dot(fNorm,ftl))/pow(d,2);
    ret += light.color*light.power*pow(max(0.0,dot(fNorm,hw)),32)/pow(d,2);
    return ret;
}

void main()
{
    vec3 tc = texture(imageTexture,fTexturePoint).xyz;
    vec3 ret = 0.2*tc.xyz;
    for (int i = 0;i < LIGHT_SIZE;i++)
    {
        ret += calcPointLight(lights[i],fPosition,fNormal,tc);
    }
    color = vec4(ret,1.0);
}
"""
