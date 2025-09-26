from OpenGL.GL import GL_RGBA
from OpenGL.GL import GL_RGBA8
from OpenGL.GL import GL_TEXTURE0
from OpenGL.GL import GL_TEXTURE_2D
from OpenGL.GL import GL_TEXTURE_MAG_FILTER
from OpenGL.GL import GL_TEXTURE_MIN_FILTER
from OpenGL.GL import GL_TEXTURE_WRAP_S
from OpenGL.GL import GL_TEXTURE_WRAP_T
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import glActiveTexture
from OpenGL.GL import glBindTexture
from OpenGL.GL import glCreateTextures
from OpenGL.GL import glDeleteTextures
from OpenGL.GL import glGenerateTextureMipmap
from OpenGL.GL import glTextureParameteri
from OpenGL.GL import glTextureStorage2D
from OpenGL.GL import glTextureSubImage2D
from OpenGL.constant import IntConstant as glIntConstant
from PySide6.QtGui import QImage
from ctypes import c_uint


class Texture2D:

    def __init__(self,levels:int,width:int,height:int):
        if (
            levels <= 0
            or width <= 0
            or height <= 0
            ):
            raise RuntimeError
        id = c_uint()
        glCreateTextures(GL_TEXTURE_2D,1,id)
        self.__id = id.value
        glTextureStorage2D(self.__id,levels,GL_RGBA8,width,height)
        self.__width = width
        self.__height = height

    def __del__(self):
        glDeleteTextures(1,(self.__id,))

    def bind(self,binding:int) -> None:
        if binding < 0:
            raise RuntimeError
        glActiveTexture(GL_TEXTURE0+binding)
        glBindTexture(GL_TEXTURE_2D,self.__id)

    def load(self,image:QImage) -> None:
        if (
            image.width() > self.__width
            or image.height() > self.__height
            ):
            raise RuntimeError
        if image.format() != QImage.Format_RGBA8888:
            image.convertTo(QImage.Format_RGBA8888)
        glTextureSubImage2D(
            self.__id
            ,0
            ,0
            ,0
            ,image.width()
            ,image.height()
            ,GL_RGBA
            ,GL_UNSIGNED_BYTE
            ,image.bits()
            )
        glGenerateTextureMipmap(self.__id)

    def setMagnifyFilter(self,value:glIntConstant) -> None:
        glTextureParameteri(self.__id,GL_TEXTURE_MAG_FILTER,value)

    def setMinifyFilter(self,value:glIntConstant) -> None:
        glTextureParameteri(self.__id,GL_TEXTURE_MIN_FILTER,value)

    def setWrapS(self,value:glIntConstant) -> None:
        glTextureParameteri(self.__id,GL_TEXTURE_WRAP_S,value)

    def setWrapT(self,value:glIntConstant) -> None:
        glTextureParameteri(self.__id,GL_TEXTURE_WRAP_T,value)

