from OpenGL.GL import GL_ARRAY_BUFFER
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_STATIC_DRAW
from OpenGL.GL import glBindVertexArray
from OpenGL.GL import glDeleteVertexArrays
from OpenGL.GL import glDrawArrays
from OpenGL.GL import glEnableVertexAttribArray
from OpenGL.GL import glGenVertexArrays
from OpenGL.GL import glVertexAttribPointer
from OpenGL.constant import IntConstant as glIntConstant
from ctypes import c_float
from ctypes import c_void_p
from opengl import Buffer


class Attribute:

    GL_FLOAT = GL_FLOAT

    def __init__(self,location:int,type:glIntConstant,size:int,offset:int):
        if (
            location < 0
            or size <= 0
            or offset < 0
            ):
            print(location,size,offset)
            raise RuntimeError
        self.location = location
        self.type = type
        self.size = size
        self.offset = offset

    def bytesize(self) -> int:
        match self.type:
            case self.GL_FLOAT:
                return 4*self.size
            case _:
                raise RuntimeError


class VertexArray:

    def __init__(self,mode:glIntConstant,attributes = []):
        self.__id = glGenVertexArrays(1)
        self.__mode = mode
        self.__attributes = [Attribute(a[0],a[1],a[2],a[3]) for a in attributes]
        self.__created = False

    def __del__(self):
        glDeleteVertexArrays(1,(self.__id,))

    def __enter__(self):
        if not self.__created:
            raise RuntimeError
        glBindVertexArray(self.__id)
        return self

    def __exit__(self,type,value,tb):
        glBindVertexArray(0)
        return False

    def add(self,location:int,type:glIntConstant,size:int,offset:int) -> None:
        self.__attributes.append(Attribute(location,type,size,offset))

    def createWithFloats(self,floats:list) -> None:
        if (
            self.__created
            or not self.__attributes
            ):
            raise RuntimeError
        stride = 0
        for attr in self.__attributes:
            if attr.type != GL_FLOAT:
                raise RuntimeError
            stride += attr.size
        if (len(floats)%stride) != 0:
            raise RuntimeError
        self.__size = len(floats)//stride
        data = (c_float*len(floats))(*floats)
        self.__buffer = Buffer.fromData(data,GL_STATIC_DRAW)
        glBindVertexArray(self.__id)
        self.__buffer.bind(GL_ARRAY_BUFFER)
        for attr in self.__attributes:
            glEnableVertexAttribArray(attr.location)
            glVertexAttribPointer(
                attr.location
                ,attr.size
                ,GL_FLOAT
                ,GL_FALSE
                ,4*stride
                ,c_void_p(attr.offset)
                )
        self.__created = True

    def draw(self,count:int = 0,mode = None) -> None:
        if (
            not self.__created
            or count < 0
            or count > self.__size
            ):
            raise RuntimeError
        glDrawArrays(self.__mode if mode is None else mode,0,count if count else self.__size)
