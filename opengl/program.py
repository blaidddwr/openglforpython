from OpenGL.GL import GL_COMPILE_STATUS
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_INVALID_INDEX
from OpenGL.GL import GL_LINK_STATUS
from OpenGL.GL import GL_SHADER_STORAGE_BLOCK
from OpenGL.GL import glAttachShader
from OpenGL.GL import glCompileShader
from OpenGL.GL import glCreateProgram
from OpenGL.GL import glCreateShader
from OpenGL.GL import glDeleteProgram
from OpenGL.GL import glDeleteShader
from OpenGL.GL import glGetAttribLocation
from OpenGL.GL import glGetProgramInfoLog
from OpenGL.GL import glGetProgramResourceIndex
from OpenGL.GL import glGetProgramiv
from OpenGL.GL import glGetShaderInfoLog
from OpenGL.GL import glGetShaderiv
from OpenGL.GL import glGetUniformBlockIndex
from OpenGL.GL import glGetUniformLocation
from OpenGL.GL import glLinkProgram
from OpenGL.GL import glShaderSource
from OpenGL.GL import glShaderStorageBlockBinding
from OpenGL.GL import glUniform1i
from OpenGL.GL import glUniform3f
from OpenGL.GL import glUniformBlockBinding
from OpenGL.GL import glUniformMatrix4fv
from OpenGL.GL import glUseProgram
from OpenGL.constant import IntConstant as glIntConstant
from PySide6.QtGui import QMatrix4x4

class SSBlock:

    def __init__(self,program,index:int):
        if index == GL_INVALID_INDEX:
            raise RuntimeError
        self.__program = program
        self.__index = index

    def setBlockBinding(self,binding:int) -> None:
        glShaderStorageBlockBinding(self.__program,self.__index,binding)


class SSBlockHandler:

    def __init__(self,program):
        self.__program = program

    def __getattr__(self,name:str):
        return SSBlock(
            self.__program
            ,glGetProgramResourceIndex(self.__program,GL_SHADER_STORAGE_BLOCK,name)
            )


class Uniform:

    def __init__(self,location:int):
        if location == -1:
            raise RuntimeError
        self.__location = location

    def set1i(self,v0) -> None:
        glUniform1i(self.__location,v0)

    def set3f(self,v0,v1,v2) -> None:
        glUniform3f(self.__location,v0,v1,v2)

    def setMatrix4f(self,value:QMatrix4x4) -> None:
        glUniformMatrix4fv(self.__location,1,GL_FALSE,value.data())


class UniformHandler:

    def __init__(self,program):
        self.__program = program

    def __getattr__(self,name:str):
        return Uniform(glGetUniformLocation(self.__program,name))


class UniformBlock:

    def __init__(self,program,index:int):
        if index == -1:
            raise RuntimeError
        self.__program = program
        self.__index = index

    def setBlockBinding(self,binding:int) -> None:
        glUniformBlockBinding(self.__program,self.__index,binding)


class UniformBlockHandler:

    def __init__(self,program):
        self.__program = program

    def __getattr__(self,name:str):
        return UniformBlock(self.__program,glGetUniformBlockIndex(self.__program,name))


class Program:

    def __init__(self,*shaders):
        self.__id = glCreateProgram()
        for s in shaders:
            if not isinstance(s,Shader):
                raise RuntimeError
            glAttachShader(self.__id,s.id())
        glLinkProgram(self.__id)
        linked = glGetProgramiv(self.__id,GL_LINK_STATUS)
        if not linked:
            info = glGetProgramInfoLog(self.__id).decode()
            print(f"Error linking program:\n{info}")
            glDeleteProgram(self.__id)
            raise RuntimeError
        self.uniform = UniformHandler(self.__id)
        self.ubo = UniformBlockHandler(self.__id)
        self.ssbo = SSBlockHandler(self.__id)

    def __del__(self):
        glDeleteProgram(self.__id)

    def __enter__(self):
        glUseProgram(self.__id)
        return self

    def __exit__(self,type,value,tb):
        glUseProgram(0)
        return False

    def __getattr__(self,name:str):
        ret = glGetAttribLocation(self.__id,name)
        if ret == -1:
            raise RuntimeError
        return ret

    def setSamplerBinding(self,name:str,binding:int) -> None:
        if binding < 0:
            raise RuntimeError
        glUniform1i(glGetUniformLocation(self.__id,name),binding)


class Shader:

    @staticmethod
    def fromFile(path:str,type:glIntConstant):
        with open(path,"r") as file:
            return Shader(file.readall(),type)

    def __init__(self,source:str,type:glIntConstant):
        self.__id = glCreateShader(type)
        glShaderSource(self.__id,source)
        glCompileShader(self.__id)
        success = glGetShaderiv(self.__id,GL_COMPILE_STATUS)
        if not success:
            info = glGetShaderInfoLog(self.__id).decode()
            print(f"Shader compilation failed:\n{info}")
            glDeleteShader(self.__id)
            raise RuntimeError

    def __del__(self):
        glDeleteShader(self.__id)

    def id(self):
        return self.__id
