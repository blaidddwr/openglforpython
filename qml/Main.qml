import QtQuick
import QtQuick.Controls
import internal

ApplicationWindow {
    width: 800
    height: 600
    visible: true
    title: qsTr("OpenGL in Python")
    OpenGLToneMapping {
        anchors.fill: parent
    }
}
