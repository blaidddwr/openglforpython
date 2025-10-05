from PySide6.QtCore import QObject
from PySide6.QtCore import QRunnable
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot
from PySide6.QtQuick import QQuickItem
from PySide6.QtQuick import QQuickWindow
from base import Renderer


class CleanupJob(QRunnable):

    def __init__(self,renderer):
        super().__init__()
        self.__renderer = renderer

    def run(self):
        del self.__renderer


class Item(QQuickItem):

    def __init__(self,parent:QObject = None):
        super().__init__(parent)
        self.__renderer = None
        self.windowChanged.connect(self.__onWindowChanged)

    def releaseResources(self):
        self.window().scheduleRenderJob(
            CleanupJob(self.__renderer)
            ,QQuickWindow.BeforeSynchronizingStage
            )
        self.__renderer = None

    def _createRenderer(self) -> Renderer:
        return Renderer()

    def _sync(self,renderer:Renderer) -> None:
        pass

    @Slot()
    def __cleanup(self):
        del self.__renderer
        self.__renderer = None

    @Slot(QQuickWindow)
    def __onWindowChanged(self,window:QQuickWindow):
        if window:
            window.beforeSynchronizing.connect(self.__sync,Qt.DirectConnection)
            window.sceneGraphInvalidated.connect(self.__cleanup,Qt.DirectConnection)
            self.__sync()
            self.__renderer.setWindow(window)

    @Slot()
    def __sync(self):
        if not self.__renderer:
            self.__renderer = self._createRenderer()
        self.__renderer.setViewportSize(self.window().size()*self.window().devicePixelRatio())
        self.__renderer.setVisible(self.isVisible())
        self._sync(self.__renderer)
