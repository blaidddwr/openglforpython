from OpenGL.GL import glViewport
from PySide6.QtCore import QObject
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtQuick import QQuickWindow


class Renderer(QObject):

    def __init__(self):
        super().__init__()
        self.__viewPortSize = QSize()
        self.__window = None
        self.__initd = False
        self.__resized = False

    def __del__(self):
        if self.__initd:
            self._destroy()

    def viewportSize(self) -> QSize:
        return self.__viewPortSize

    def window(self) -> QQuickWindow:
        if self.__window is None:
            raise RuntimeError
        return self.__window

    def setViewportSize(self,value:QSize) -> None:
        if self.__viewPortSize != value:
            self.__viewPortSize = value
            self.__resized = True

    def setWindow(self,window:QQuickWindow) -> None:
        self.__window = window
        if window:
            window.beforeRendering.connect(self.__init,Qt.DirectConnection)
            window.beforeRenderPassRecording.connect(self.__paint,Qt.DirectConnection)

    def _destroy(self):
        pass

    def _init(self):
        pass

    def _paint(self):
        pass

    def _resize(self):
        pass

    def __init(self):
        if not self.__initd:
            self._init()
            self.__initd = True

    def __paint(self):
        if self.__window is None:
            raise RuntimeError
        self.__window.beginExternalCommands()
        glViewport(0,0,self.__viewPortSize.width(),self.__viewPortSize.height())
        if self.__resized:
            self._resize()
        self._paint()
        self.__window.endExternalCommands()
