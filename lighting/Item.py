from PySide6.QtCore import QObject
from PySide6.QtCore import QTimerEvent
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from lighting.renderer import Renderer
import base


class Item(base.Item):

    def __init__(self,parent:QObject = None):
        super().__init__(parent)
        self.startTimer(16)
        self.__cubeSpinning = False
        self.__angle = 0
        self.__theta = 0
        self.__phi = 0
        self.setAcceptedMouseButtons(Qt.LeftButton)

    def mouseDoubleClickEvent(self,event:QMouseEvent) -> None:
        self.__cubeSpinning = not self.__cubeSpinning
        event.accept()

    def mouseMoveEvent(self,event:QMouseEvent) -> None:
        dx = self.__mouseStartX-event.globalPosition().x()
        dy = self.__mouseStartY-event.globalPosition().y()
        dx = dx/self.window().width()
        dy = dy/self.window().height()
        self.__theta = self.__thetaStart+dx*360
        if self.__theta < 0:
            self.__theta += 360
        elif self.__theta >= 360:
            self.__theta -= 360
        self.__phi = max(0,min(180,self.__phiStart+dy*360))
        self.window().update()
        event.accept()

    def mousePressEvent(self,event:QMouseEvent) -> None:
        self.__mouseStartX = event.globalPosition().x()
        self.__mouseStartY = event.globalPosition().y()
        self.__thetaStart = self.__theta
        self.__phiStart = self.__phi
        event.accept()

    def timerEvent(self,event:QTimerEvent) -> None:
        if self.__cubeSpinning:
            self.__angle += 0.5
            self.window().update()

    def _createRenderer(self) -> base.Renderer:
        return Renderer()

    def _sync(self,renderer:base.Renderer) -> None:
        renderer.setAngle(self.__angle)
        renderer.setTheta(self.__theta)
        renderer.setPhi(self.__phi)
