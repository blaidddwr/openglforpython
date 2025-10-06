from PySide6.QtGui import QGuiApplication
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQml import qmlRegisterType
from PySide6.QtQuick import QQuickView
from PySide6.QtQuick import QSGRendererInterface
from pathlib import Path
import alphaBlend
import camera
import compute
import instanced
import lighting
import procedural
import ssbo
import sys
import texture1D
import texture2D
import texture2DArray
import toneMapping
import transform
import triangle


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    QQuickView.setGraphicsApi(QSGRendererInterface.OpenGL)
    format = QSurfaceFormat()
    format.setVersion(4,5)
    format.setProfile(QSurfaceFormat.CoreProfile)
    format.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
    QSurfaceFormat.setDefaultFormat(format)
    qmlRegisterType(triangle.Item,"internal",1,0,"OpenGLTriangle")
    qmlRegisterType(texture2D.Item,"internal",1,0,"OpenGLTexture2D")
    qmlRegisterType(alphaBlend.Item,"internal",1,0,"OpenGLAlphaBlend")
    qmlRegisterType(transform.Item,"internal",1,0,"OpenGLTransform")
    qmlRegisterType(camera.Item,"internal",1,0,"OpenGLCamera")
    qmlRegisterType(lighting.Item,"internal",1,0,"OpenGLLighting")
    qmlRegisterType(instanced.Item,"internal",1,0,"OpenGLInstanced")
    qmlRegisterType(texture2DArray.Item,"internal",1,0,"OpenGLTexture2DArray")
    qmlRegisterType(toneMapping.Item,"internal",1,0,"OpenGLToneMapping")
    qmlRegisterType(ssbo.Item,"internal",1,0,"OpenGLSSBO")
    qmlRegisterType(compute.Item,"internal",1,0,"OpenGLCompute")
    qmlRegisterType(texture1D.Item,"internal",1,0,"OpenGLTexture1D")
    qmlRegisterType(procedural.Item,"internal",1,0,"OpenGLProcedural")
    engine = QQmlApplicationEngine()
    engine.load(Path(__file__).resolve().parent/"qml"/"Main.qml")
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
