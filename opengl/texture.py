from OpenGL.GL import GL_RGBA
from OpenGL.GL import GL_RGBA8
from OpenGL.GL import GL_TEXTURE0
from OpenGL.GL import GL_TEXTURE_1D
from OpenGL.GL import GL_TEXTURE_2D
from OpenGL.GL import GL_TEXTURE_2D_ARRAY
from OpenGL.GL import GL_TEXTURE_MAG_FILTER
from OpenGL.GL import GL_TEXTURE_MIN_FILTER
from OpenGL.GL import GL_TEXTURE_WRAP_R
from OpenGL.GL import GL_TEXTURE_WRAP_S
from OpenGL.GL import GL_TEXTURE_WRAP_T
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import glActiveTexture
from OpenGL.GL import glBindTexture
from OpenGL.GL import glCreateTextures
from OpenGL.GL import glDeleteTextures
from OpenGL.GL import glGenerateTextureMipmap
from OpenGL.GL import glTextureParameteri
from OpenGL.GL import glTextureStorage1D
from OpenGL.GL import glTextureStorage2D
from OpenGL.GL import glTextureStorage3D
from OpenGL.GL import glTextureSubImage1D
from OpenGL.GL import glTextureSubImage2D
from OpenGL.GL import glTextureSubImage3D
from OpenGL.constant import IntConstant as glIntConstant
from PySide6.QtGui import QImage
from ctypes import c_ubyte
from ctypes import c_uint


class Texture:

    def __init__(self,type:glIntConstant):
        id = c_uint()
        glCreateTextures(type,1,id)
        self.__id = id.value
        self.__type = type

    def __del__(self):
        glDeleteTextures(1,(self.__id,))

    def bind(self,binding:int) -> None:
        if binding < 0:
            raise RuntimeError
        glActiveTexture(GL_TEXTURE0+binding)
        glBindTexture(self.__type,self.__id)

    def id(self):
        return self.__id

    def setMagnifyFilter(self,value:glIntConstant) -> None:
        glTextureParameteri(self.__id,GL_TEXTURE_MAG_FILTER,value)

    def setMinifyFilter(self,value:glIntConstant) -> None:
        glTextureParameteri(self.__id,GL_TEXTURE_MIN_FILTER,value)

    def setWrapS(self,value:glIntConstant) -> None:
        glTextureParameteri(self.__id,GL_TEXTURE_WRAP_S,value)

    def setWrapT(self,value:glIntConstant) -> None:
        glTextureParameteri(self.__id,GL_TEXTURE_WRAP_T,value)

    def setWrapR(self,value:glIntConstant) -> None:
        glTextureParameteri(self.__id,GL_TEXTURE_WRAP_R,value)


class Texture1D(Texture):

    @staticmethod
    def fromArray(levels:int,colors:list):
        if (len(colors)%4) != 0:
            raise RuntimeError
        ret = Texture1D(levels,GL_RGBA8,len(colors)//4)
        ret.loadArray(colors)
        return ret

    def __init__(self,levels:int,format:glIntConstant,width:int):
        if (
            levels <= 0
            or width <= 0
            ):
            raise RuntimeError
        super().__init__(GL_TEXTURE_1D)
        self.__format = format
        glTextureStorage1D(self.id(),levels,format,width)
        self.__width = width

    def loadArray(self,colors:list) -> None:
        size = len(colors)
        width = size//4
        if (
            self.__format != GL_RGBA8
            or width > self.__width
            or (size%4) != 0
            ):
            raise RuntimeError
        data = (c_ubyte*size)()
        for (i,v) in enumerate(colors):
            data[i] = v
        glTextureSubImage1D(
            self.id()
            ,0
            ,0
            ,width
            ,GL_RGBA
            ,GL_UNSIGNED_BYTE
            ,data
            )
        glGenerateTextureMipmap(self.id())


class Texture2D(Texture):

    @staticmethod
    def fromImage(levels:int,image:QImage):
        ret = Texture2D(levels,GL_RGBA8,image.width(),image.height())
        ret.loadImage(image)
        return ret

    def __init__(self,levels:int,format:glIntConstant,width:int,height:int):
        if (
            levels <= 0
            or width <= 0
            or height <= 0
            ):
            raise RuntimeError
        super().__init__(GL_TEXTURE_2D)
        self.__format = format
        glTextureStorage2D(self.id(),levels,format,width,height)
        self.__width = width
        self.__height = height

    def loadImage(self,image:QImage) -> None:
        if (
            self.__format != GL_RGBA8
            or image.width() > self.__width
            or image.height() > self.__height
            ):
            raise RuntimeError
        if image.format() != QImage.Format_RGBA8888:
            image.convertTo(QImage.Format_RGBA8888)
        glTextureSubImage2D(
            self.id()
            ,0
            ,0
            ,0
            ,image.width()
            ,image.height()
            ,GL_RGBA
            ,GL_UNSIGNED_BYTE
            ,image.bits()
            )
        glGenerateTextureMipmap(self.id())


class Texture2DArray(Texture):

    @staticmethod
    def fromImages(levels:int,images:list):
        if not images:
            raise RuntimeError
        ret = Texture2DArray(levels,GL_RGBA8,images[0].width(),images[0].height(),len(images))
        ret.loadImages(*images)
        return ret

    def __init__(self,levels:int,format:glIntConstant,width:int,height:int,layerSize:int):
        if (
            levels <= 0
            or width <= 0
            or height <= 0
            or layerSize <= 0
            ):
            raise RuntimeError
        super().__init__(GL_TEXTURE_2D_ARRAY)
        self.__format = format
        glTextureStorage3D(self.id(),levels,format,width,height,layerSize)
        self.__width = width
        self.__height = height
        self.__depth = layerSize

    def loadImages(self,*images) -> None:
        for (layer,img) in enumerate(images):
            if (
                self.__format != GL_RGBA8
                or img.width() > self.__width
                or img.height() > self.__height
                or layer > self.__depth
                ):
                raise RuntimeError
            if img.format() != QImage.Format_RGBA8888:
                img.convertTo(QImage.Format_RGBA8888)
            glTextureSubImage3D(
                self.id()
                ,0
                ,0
                ,0
                ,layer
                ,img.width()
                ,img.height()
                ,1
                ,GL_RGBA
                ,GL_UNSIGNED_BYTE
                ,img.bits()
                )
        glGenerateTextureMipmap(self.id())
