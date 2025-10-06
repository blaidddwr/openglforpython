import QtQuick
import QtQuick.Controls
import internal

ApplicationWindow {
    width: 800
    height: 600
    visible: true
    title: qsTr("OpenGL in Python")
    Loader {
        anchors.fill: parent
        sourceComponent: openGLTexture1D
    }
    Component { id: openGLTriangle; OpenGLTriangle {} }
    Component { id: openGLTexture2D; OpenGLTexture2D {} }
    Component { id: openGLAlphaBlend; OpenGLAlphaBlend {} }
    Component { id: openGLTransform; OpenGLTransform {} }
    Component { id: openGLCamera; OpenGLCamera {} }
    Component { id: openGLLighting; OpenGLLighting {} }
    Component { id: openGLInstanced; OpenGLInstanced {} }
    Component { id: openGLTexture2DArray; OpenGLTexture2DArray {} }
    Component { id: openGLToneMapping; OpenGLToneMapping {} }
    Component { id: openGLSSBO; OpenGLSSBO {} }
    Component { id: openGLCompute; OpenGLCompute {} }
    Component { id: openGLTexture1D; OpenGLTexture1D {} }
}
