from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FRAGMENT_SHADER
from OpenGL.GL import GL_LINEAR
from OpenGL.GL import GL_NEAREST
from OpenGL.GL import GL_REPEAT
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import glClear
from OpenGL.GL import glViewport
from opengl import Program
from opengl import Shader
from opengl import Texture2D
from opengl import VertexArray
import base


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
        with self.__program:
            with self.__vao as vao:
                self.__texture.bind(0)
                vao.draw()
        glClear(GL_DEPTH_BUFFER_BIT)

    def _destroy(self):
        del self.__texture
        del self.__vao
        del self.__program

    def __initProgram(self):
        self.__program = Program(
            Shader(_vertexShaderSrc,GL_VERTEX_SHADER)
            ,Shader(_fragmentShaderSrc,GL_FRAGMENT_SHADER)
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
            program._imageTexture.set1i(0)

    def __initVertices(self):
        vertices = (
            -0.5,-0.5,0.0,1.0,0.0,0.0,0.0,1.0
            ,0.5,-0.5,0.0,0.0,1.0,0.0,1.0,1.0
            ,0.0,0.5,0.0,0.0,0.0,1.0,0.5,0.0
        )
        with self.__program as program:
            self.__vao = VertexArray(
                GL_TRIANGLES
                ,(
                    (program.position,GL_FLOAT,3,0)
                    ,(program.color,GL_FLOAT,3,12)
                    ,(program.texturePoint,GL_FLOAT,2,24)
                    )
                )
            self.__vao.createWithFloats(vertices)


_vertexShaderSrc = """#version 430 core

in vec3 position;
in vec3 color;
in vec2 texturePoint;

out vec3 fColor;
out vec2 fTexturePoint;

void main()
{
    gl_Position = vec4(position,1.0);
    fColor = color;
    fTexturePoint = texturePoint;
}
"""

_fragmentShaderSrc = """#version 430 core

in vec3 fColor;
in vec2 fTexturePoint;

uniform sampler2D imageTexture;

out vec4 color;

void main()
{
    color = vec4(fColor,1.0)*texture(imageTexture,fTexturePoint);
}
"""
