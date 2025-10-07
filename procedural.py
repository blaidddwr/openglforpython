from OpenGL.GL import GL_CLAMP_TO_EDGE
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FRAGMENT_SHADER
from OpenGL.GL import GL_LINEAR
from OpenGL.GL import GL_NEAREST
from OpenGL.GL import GL_STATIC_DRAW
from OpenGL.GL import GL_TRIANGLE_STRIP
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import glClear
from OpenGL.GL import glViewport
from PySide6.QtCore import QObject
from PySide6.QtCore import Qt
from PySide6.QtGui import QMatrix4x4
from PySide6.QtGui import QMouseEvent
from ctypes import Structure as cStructure
from ctypes import c_char
from ctypes import c_float
from ctypes import c_uint
from opengl import Buffer
from opengl import Program
from opengl import Shader
from opengl import Texture1D
from opengl import VertexArray
from random import uniform as randUniform
import base

SINE_SIZE = 20


class Item(base.Item):

    def __init__(self,parent:QObject = None):
        super().__init__(parent)
        self.setAcceptedMouseButtons(Qt.LeftButton)

    def mousePressEvent(self,event:QMouseEvent) -> None:
        self.window().update()
        event.accept()

    def _createRenderer(self) -> base.Renderer:
        return Renderer()

    def _sync(self,renderer:base.Renderer) -> None:
        renderer.updateSines()


class Sine(cStructure):
    _fields_ = [
        ("amplitude",c_float)
        ,("dropoff",c_float)
        ,("position",c_float*2)
        ,("frequency",c_float)
        ,("phase",c_float)
    ]
    _pack_ = 1


class Sines(cStructure):
    _fields_ = [
        ("size",c_uint)
        ,("p0",c_char*4)
        ,("sines",Sine*SINE_SIZE)
    ]
    _pack_ = 1


class Renderer(base.Renderer):

    def __init__(self):
        super().__init__()
        self.__projection = None
        self.__updateSines = True

    def updateSines(self):
        self.__updateSines = True

    def _init(self):
        self.__initProgram()
        self.__initVertices()
        self.__initTexture()
        self.__initSines()

    def _destroy(self):
        del self.__sinesSSBO
        del self.__texture
        del self.__vao
        del self.__program

    def _paint(self):
        if self.__updateSines:
            for sine in self.__sines.sines:
                sine.amplitude = randUniform(0,5)
                sine.dropoff = randUniform(1,10)
                sine.position = (randUniform(-2,2),randUniform(-2,2))
                sine.frequency = randUniform(0.1,1)
                sine.phase = randUniform(0,6.28)
            self.__sinesSSBO.write(0,self.__sines)
            self.__updateSines = False
        glViewport(0,0,self.viewportSize().width(),self.viewportSize().height())
        with self.__program:
            if self.__projection is None:
                self.__projection = QMatrix4x4()
                a = self.aspectRatio()
                self.__projection.ortho(-a,a,-1,1,-1,1)
                self.__projectionUniform.setMatrix4f(self.__projection)
            with self.__vao as vao:
                self.__sinesSSBO.bindToShaderStorage(0)
                self.__texture.bind(0)
                vao.draw()
        glClear(GL_DEPTH_BUFFER_BIT)

    def _resize(self):
        self.__projection = None

    def __initProgram(self):
        self.__program = Program(
            Shader(_vertexShaderSrc,GL_VERTEX_SHADER)
            ,Shader(_fragmentShaderSrc,GL_FRAGMENT_SHADER)
            )
        with self.__program as program:
            self.__projectionUniform = program.uniform.projection

    def __initSines(self):
        self.__sines = Sines()
        self.__sines.size = SINE_SIZE
        self.__sinesSSBO = Buffer.fromData(self.__sines,GL_STATIC_DRAW)
        with self.__program as program:
            program.ssbo.SineBuffer.setBlockBinding(0)

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
            -0.9,-0.9,0.0,0.0,1.0
            ,0.9,-0.9,0.0,1.0,1.0
            ,-0.9,0.9,0.0,0.0,0.0
            ,0.9,0.9,0.0,1.0,0.0
        )
        with self.__program as program:
            self.__vao = VertexArray.fromFloats(
                vertices
                ,GL_TRIANGLE_STRIP
                ,(
                    (program.position,3,GL_FLOAT,20,0)
                    ,(program.texturePoint,2,GL_FLOAT,20,12)
                    )
                )


_vertexShaderSrc = """#version 430 core

in vec3 position;
in vec2 texturePoint;

uniform mat4 projection;

out vec2 fTexturePoint;

void main()
{
    gl_Position = projection*vec4(position,1.0);
    fTexturePoint = texturePoint;
}
"""

_fragmentShaderSrc = """#version 430 core

const float PI = 3.14159265358979323846;

struct Sine
{
    float amplitude;
    float dropoff;
    vec2 position;
    float frequency;
    float phase;
};

in vec2 fTexturePoint;

layout(std430) buffer SineBuffer
{
    uint sineSize;
    Sine sines[];
};

uniform sampler1D imageTexture;

out vec4 color;

void main()
{
    float f = 0.0;
    for (uint i = 0;i < sineSize;i++)
    {
        float l = distance(fTexturePoint,sines[i].position);
        float d = 1+cos(max(PI,PI*l*sines[i].dropoff));
        f += sines[i].amplitude*d*0.5*(1.0+sin((2.0*PI*sines[i].frequency*l)+sines[i].phase));
    }
    bool isOdd = ((int(f)%2) == 1);
    color = texture(imageTexture,isOdd ? 1.0 - fract(f) : fract(f));
}
"""
