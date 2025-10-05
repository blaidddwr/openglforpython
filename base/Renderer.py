from OpenGL.GL import glViewport
from PySide6.QtCore import QObject
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from PySide6.QtQuick import QQuickWindow
from pathlib import Path
import inspect


class Renderer(QObject):

    def __init__(self):
        super().__init__()
        self.__viewPortSize = QSize()
        self.__window = None
        self.__initd = False
        self.__resized = False
        self.__visible = False

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

    def setVisible(self,value:bool) -> None:
        self.__visible = value

    def setWindow(self,window:QQuickWindow) -> None:
        self.__window = window
        if window:
            window.beforeRendering.connect(self.__init,Qt.DirectConnection)
            window.beforeRenderPassRecording.connect(self.__paint,Qt.DirectConnection)

    def _destroy(self):
        pass

    @staticmethod
    def _image(fileName:str) -> QImage:
        ret = QImage(Path(__file__).resolve().parent.parent/"gfx"/fileName)
        ret = ret.convertToFormat(QImage.Format_RGBA8888)
        return ret

    def _init(self):
        pass

    def _paint(self):
        pass

    def _resize(self):
        pass

    def _shader(self,fileName:str):
        with open(Path(inspect.getfile(self.__class__)).resolve().parent/fileName,"r") as file:
            return file.read()

    def __init(self):
        if not self.__initd:
            self._init()
            self.__initd = True

    def __paint(self):
        if self.__window is None:
            raise RuntimeError
        if not self.__visible:
            return
        self.__window.beginExternalCommands()
        glViewport(0,0,self.__viewPortSize.width(),self.__viewPortSize.height())
        if self.__resized:
            self._resize()
        self._paint()
        self.__window.endExternalCommands()
