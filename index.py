import sys
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg

uiclass, baseclass = pg.Qt.loadUiType("main.ui")

class MainWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()