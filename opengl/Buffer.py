from OpenGL.GL import GL_SHADER_STORAGE_BUFFER
from OpenGL.GL import GL_UNIFORM_BUFFER
from OpenGL.GL import glBindBuffer
from OpenGL.GL import glBindBufferBase
from OpenGL.GL import glCreateBuffers
from OpenGL.GL import glDeleteBuffers
from OpenGL.GL import glGetNamedBufferSubData
from OpenGL.GL import glNamedBufferData
from OpenGL.GL import glNamedBufferSubData
from OpenGL.constant import IntConstant as glIntConstant
from ctypes import addressof
from ctypes import byref
from ctypes import c_float
from ctypes import c_uint
from ctypes import c_void_p
from ctypes import sizeof


class Buffer:

    @staticmethod
    def fromData(data,usage:glIntConstant):
        ret = Buffer(sizeof(data),usage)
        ret.write(0,data)
        return ret

    @classmethod
    def fromFloats(cls,floats,usage:glIntConstant):
        data = (c_float*len(floats))(*floats)
        return cls.fromData(data,usage)

    def __init__(self,size:int,usage:glIntConstant):
        if size <= 0:
            raise RuntimeError
        id = c_uint()
        glCreateBuffers(1,id)
        self.__id = id.value
        glNamedBufferData(self.__id,size,None,usage)

    def __del__(self):
        glDeleteBuffers(1,(self.__id,))

    def write(self,offset:int,data) -> None:
        size = sizeof(data)
        if (
            offset < 0
            or size <= 0
            ):
            raise RuntimeError
        glNamedBufferSubData(self.__id,offset,size,byref(data))

    def read(self,offset:int,data) -> None:
        size = sizeof(data)
        if (
            offset < 0
            or size <= 0
            ):
            raise RuntimeError
        glGetNamedBufferSubData(self.__id,offset,size,c_void_p(addressof(data)))

    def bind(self,target:glIntConstant) -> None:
        glBindBuffer(target,self.__id)

    def bindToShaderStorage(self,index:int) -> None:
        if index < 0:
            raise RuntimeError
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER,index,self.__id)

    def bindToUniform(self,index:int) -> None:
        if index < 0:
            raise RuntimeError
        glBindBufferBase(GL_UNIFORM_BUFFER,index,self.__id)
