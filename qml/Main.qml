import QtQuick
import QtQuick.Controls
import internal

ApplicationWindow {
    width: 800
    height: 600
    visible: true
    title: qsTr("OpenGL in Python")
    Component.onCompleted: openGLSSBO.visible = true
    OpenGLTriangle {
        id: openGLTriangle
        anchors.fill: parent
        visible: false
    }
    OpenGLTexture2D {
        id: openGLTexture2D
        anchors.fill: parent
        visible: false
    }
    OpenGLAlphaBlend {
        id: openGLAlphaBlend
        anchors.fill: parent
        visible: false
    }
    OpenGLTransform {
        id: openGLTransform
        anchors.fill: parent
        visible: false
    }
    OpenGLCamera {
        id: openGLCamera
        anchors.fill: parent
        visible: false
    }
    OpenGLLighting {
        id: openGLLighting
        anchors.fill: parent
        visible: false
    }
    OpenGLInstanced {
        id: openGLInstanced
        anchors.fill: parent
        visible: false
    }
    OpenGLTexture2DArray {
        id: openGL2DArray
        anchors.fill: parent
        visible: false
    }
    OpenGLToneMapping {
        id: openGLToneMapping
        anchors.fill: parent
        visible: false
    }
    OpenGLSSBO {
        id: openGLSSBO
        anchors.fill: parent
        visible: false
    }
}
