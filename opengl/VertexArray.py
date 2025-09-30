from OpenGL.GL import GL_ARRAY_BUFFER
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_STATIC_DRAW
from OpenGL.GL import glBindVertexArray
from OpenGL.GL import glDeleteVertexArrays
from OpenGL.GL import glDrawArrays
from OpenGL.GL import glDrawArraysInstanced
from OpenGL.GL import glEnableVertexAttribArray
from OpenGL.GL import glGenVertexArrays
from OpenGL.GL import glVertexAttribDivisor
from OpenGL.GL import glVertexAttribPointer
from OpenGL.constant import IntConstant as glIntConstant
from ctypes import c_void_p
from opengl import Buffer


class VertexArray:

    @staticmethod
    def fromFloats(floats:list,mode:glIntConstant,attributes:list,instanceSize:int = 1):
        if (
            not floats
            or not attributes
            ):
            raise RuntimeError
        stride = None
        for a in attributes:
            if (
                len(a) < 5
                or len(a) > 6
                ):
                raise RuntimeError
            if stride is None:
                stride = a[3]
            elif stride != a[3]:
                raise RuntimeError
        if ((4*len(floats))%stride) != 0:
            raise RuntimeError
        size = (4*len(floats))//stride
        buffer = Buffer.fromFloats(floats,GL_STATIC_DRAW)
        buffer.bind(GL_ARRAY_BUFFER)
        ret = VertexArray(mode,size,instanceSize,attributes)
        ret.__buffer = buffer
        return ret

    def __init__(self,mode:glIntConstant,size:int,instanceSize:int = 1,attributes:list = []):
        if (
            size <= 0
            or instanceSize <= 0
            ):
            raise RuntimeError
        self.__id = glGenVertexArrays(1)
        self.__mode = mode
        self.__size = size
        self.__instanceSize = instanceSize
        self.__active = False
        if attributes:
            self.__active = True
            glBindVertexArray(self.__id)
            for a in attributes:
                self.add(*a)
            glBindVertexArray(0)
            self.__active = False

    def __del__(self):
        glDeleteVertexArrays(1,(self.__id,))

    def __enter__(self):
        glBindVertexArray(self.__id)
        self.__active = True
        return self

    def __exit__(self,type,value,tb):
        self.__active = False
        glBindVertexArray(0)
        return False

    def add(
        self
        ,location:int
        ,size:int
        ,type:glIntConstant
        ,stride:int
        ,offset:int
        ,divisor:int = 0
        ) -> None:
        if (
            not self.__active
            or location == -1
            or divisor < 0
            ):
            raise RuntimeError
        glEnableVertexAttribArray(location)
        glVertexAttribPointer(location,size,type,GL_FALSE,stride,c_void_p(offset))
        if divisor > 0:
            glVertexAttribDivisor(location,divisor)

    def draw(self,count:int = 0,mode = None) -> None:
        if (
            not self.__active
            or count < 0
            or count > self.__size
            ):
            raise RuntimeError
        glDrawArrays(self.__mode if mode is None else mode,0,count if count else self.__size)

    def drawInstanced(self,instanceCount:int = 0,count:int = 0,mode = None) -> None:
        if (
            not self.__active
            or count < 0
            or count > self.__size
            or instanceCount < 0
            or instanceCount > self.__instanceSize
            ):
            raise RuntimeError
        glDrawArraysInstanced(
            self.__mode if mode is None else mode
            ,0
            ,count if count else self.__size
            ,instanceCount if instanceCount else self.__instanceSize
            )
