from OpenGL.GL import GL_COMPUTE_SHADER
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GL import GL_DYNAMIC_COPY
from OpenGL.GL import GL_FRAGMENT_SHADER
from OpenGL.GL import GL_POINTS
from OpenGL.GL import GL_SHADER_STORAGE_BARRIER_BIT
from OpenGL.GL import GL_VERTEX_SHADER
from OpenGL.GL import glClear
from OpenGL.GL import glDispatchCompute
from OpenGL.GL import glMemoryBarrier
from OpenGL.GL import glPointSize
from OpenGL.GL import glViewport
from PySide6.QtCore import QObject
from PySide6.QtCore import QTimerEvent
from PySide6.QtGui import QMatrix4x4
from ctypes import Structure as cStructure
from ctypes import c_char
from ctypes import c_float
from ctypes import c_uint
from opengl import Buffer
from opengl import Program
from opengl import Shader
from opengl import VertexArray
from random import uniform as randUniform
import base

PARTICLE_SIZE = 5000
VIEWSIZE = 1000


class Item(base.Item):

    def __init__(self,parent:QObject = None):
        super().__init__(parent)
        self.startTimer(16)

    def timerEvent(self,event:QTimerEvent) -> None:
        self.window().update()

    def _createRenderer(self) -> base.Renderer:
        return Renderer()


class Particle(cStructure):
    _fields_ = [
        ("position",c_float*2)
        ,("velocity",c_float*2)
        ,("mass",c_float)
        ,("charge",c_float)
    ]
    _pack_ = 1


class Particles(cStructure):
    _fields_ = [
        ("size",c_uint)
        ,("p0",c_char*4)
        ,("p",Particle*PARTICLE_SIZE)
    ]
    _pack_ = 1


class Renderer(base.Renderer):

    def __init__(self):
        super().__init__()
        self.__projection = None
        self.__bufferIndex = 0

    def _destroy(self):
        del self.__vao
        del self.__program

    def _init(self):
        self.__initProgram()
        self.__initCompute()
        self.__initParticles()
        self.__initVAO()

    def _paint(self):
        glPointSize(5*self.window().devicePixelRatio());
        glViewport(0,0,self.viewportSize().width(),self.viewportSize().height())
        outBufferIndex = int(not bool(self.__bufferIndex))
        self.__particlesSSBOs[self.__bufferIndex].bindToShaderStorage(0)
        self.__particlesSSBOs[outBufferIndex].bindToShaderStorage(1)
        with self.__compute:
            glDispatchCompute(self.__particles.size,1,1)
        with self.__program:
            with self.__vao as vao:
                if self.__projection is None:
                    self.__projection = QMatrix4x4()
                    a = self.aspectRatio()
                    self.__projection.ortho(-VIEWSIZE*a,VIEWSIZE*a,-VIEWSIZE,VIEWSIZE,-1,1)
                    self.__projectionUniform.setMatrix4f(self.__projection)
                vao.draw()
        glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
        self.__bufferIndex = outBufferIndex
        glClear(GL_DEPTH_BUFFER_BIT)

    def _resize(self):
        self.__projection = None

    def __initCompute(self):
        self.__compute = Program(Shader(_computeShaderSrc,GL_COMPUTE_SHADER))

    def __initParticles(self):
        self.__particles = Particles()
        self.__particles.size = PARTICLE_SIZE
        a = self.aspectRatio()
        for i in range(self.__particles.size):
            self.__particles.p[i].position = (randUniform(-100*a,100*a),randUniform(-100,100))
            self.__particles.p[i].velocity = (0,0)
            self.__particles.p[i].mass = randUniform(0.1,1)
            self.__particles.p[i].charge = randUniform(-1,1)
        self.__particlesSSBOs = [
            Buffer.fromData(self.__particles,GL_DYNAMIC_COPY)
            ,Buffer.fromData(self.__particles,GL_DYNAMIC_COPY)
        ]
        with self.__program as program:
            program.ssbo.ParticleBuffer.setBlockBinding(0)
        with self.__compute as program:
            program.ssbo.InParticleBuffer.setBlockBinding(0)
            program.ssbo.OutParticleBuffer.setBlockBinding(1)

    def __initProgram(self):
        self.__program = Program(
            Shader(_vertexShaderSrc,GL_VERTEX_SHADER)
            ,Shader(_fragmentShaderSrc,GL_FRAGMENT_SHADER)
            )
        with self.__program as program:
            self.__projectionUniform = program.uniform.projection

    def __initVAO(self):
        with self.__program:
            self.__vao = VertexArray(GL_POINTS,self.__particles.size)
            with self.__vao:
                pass


_vertexShaderSrc = """#version 450 core

struct Particle {
    vec2 position;
    vec2 velocity;
    float mass;
    float charge;
};

uniform mat4 projection;

layout(std430) buffer ParticleBuffer {
    uint pSize;
    Particle particles[];
};

out float fMass;
out float fCharge;

void main()
{
    gl_Position = projection*vec4(particles[gl_VertexID].position,0.0,1.0);
    fMass = particles[gl_VertexID].mass;
    fCharge = particles[gl_VertexID].charge;
}
"""

_fragmentShaderSrc = """#version 450 core

in float fMass;
in float fCharge;

out vec4 color;

void main()
{
    const vec4 nColor = vec4(1.0,0.0,0.0,1.0);
    const vec4 pColor = vec4(0.0,0.0,1.0,1.0);
    vec2 c = 2.0*gl_PointCoord-1.0;
    if (dot(c,c) > fMass)
    {
        discard;
    }
    color = fCharge < 0.0 ? nColor : pColor;
    //color = vec4(1.0);
}
"""

_computeShaderSrc = """#version 450 core

const float PI = 3.14159265358979323846;
const float dt = 5e-5;
const float RADIUS_BOUNDARY = 900.0;
const float BOUNCE_VELOCITY = 100000.0;

layout (local_size_x=1,local_size_y=1,local_size_z=1) in;

struct Particle {
    vec2 position;
    vec2 velocity;
    float mass;
    float charge;
};

layout(std430) buffer InParticleBuffer {
    uint inSize;
    Particle inParticles[];
};

layout(std430) buffer OutParticleBuffer {
    uint outSize;
    Particle outParticles[];
};

vec2 gravity(Particle self, Particle other);
vec2 electrostatic(Particle self, Particle other);
vec3 magnetic(Particle self, Particle other);
vec2 lorentz(Particle p, vec3 B);
void move(uint self, vec2 force);

void main()
{
    uint self = gl_GlobalInvocationID.x;
    if (inSize != outSize)
    {
        return;
    }
    vec2 force = vec2(0.0);
    vec3 B = vec3(0.0);
    for (uint i = 0;i < inSize;i++)
    {
        if (self != i)
        {
            force += gravity(inParticles[self],inParticles[i]);
            force += electrostatic(inParticles[self],inParticles[i]);
            B += magnetic(inParticles[self],inParticles[i]);
        }
    }
    force += lorentz(inParticles[self],B);
    move(self,force);
}

vec2 gravity(Particle self, Particle other)
{
    const float G = 6.67e-11;
    vec2 d = other.position-self.position;
    d = normalize(d)/dot(d,d);
    return G*self.mass*other.mass*d;
}

vec2 electrostatic(Particle self, Particle other)
{
    const float K = 8.99e9;
    vec2 d = self.position-other.position;
    d = normalize(d)/dot(d,d);
    return K*self.charge*other.charge*d;
}

vec3 magnetic(Particle self, Particle other)
{
    const float u = PI*4e-7;
    vec2 d = other.position-self.position;
    float r2 = dot(d,d);
    d = normalize(d);
    return cross(vec3(other.velocity,0.0),vec3(u*other.charge*d/(4.0*PI),0.0))/r2;
}

vec2 lorentz(Particle p, vec3 B)
{
    return (p.charge*cross(vec3(p.velocity,0.0),B)).xy;
}

void move(uint self, vec2 force)
{
    outParticles[self].velocity = inParticles[self].velocity+(dt*force/inParticles[self].mass);
    outParticles[self].position = inParticles[self].position+(outParticles[self].velocity*dt);
    outParticles[self].mass = inParticles[self].mass;
    outParticles[self].charge = inParticles[self].charge;
    if (distance(outParticles[self].position,vec2(0.0)) > RADIUS_BOUNDARY)
    {
        outParticles[self].position = RADIUS_BOUNDARY*normalize(outParticles[self].position);
        outParticles[self].velocity = -BOUNCE_VELOCITY*normalize(outParticles[self].position);
    }
}
"""
