import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication, QMessageBox
import pyqtgraph as pg
import pandas as pd
from pyqtgraph import PlotWidget
from managers.signal_loader import ISignalLoader, TextSignalLoader, CSVSignalLoader, ExcelXSignalLoader, ExcelSignalLoader
from models.signal import Signal

uiclass, baseclass = pg.Qt.loadUiType("main.ui")

class MainWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.handle_events()

    def handle_events(self):
        # import signal to ch1
        self.import_signal_ch1.triggered.connect(self.get_signal_file)
        # import signal to ch2
        self.import_signal_ch2.triggered.connect(self.get_signal_file)
        # draw on play
        # self.actionPlay_Pause.triggered.connect(self.draw)
        # self.play_button_1.clicked.connect(self.draw)

    def get_signal_file(self):
        # get path of signal files only of types (xls, csv, txt)
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Single File', QtCore.QDir.rootPath(), "(*.xls);;(*.txt);;(*.csv);;(*.xlsx)")

        # check the type of signal file
        file_type = file_path.split('.')[-1]

        # Picking the right loader from file_type
        loader: ISignalLoader
        if file_type == 'xls':
            loader = ExcelSignalLoader()
        elif file_type == 'xlsx':
            loader = ExcelXSignalLoader()
        elif file_type == 'csv':
            loader = CSVSignalLoader()
        else:
            loader = TextSignalLoader()
        
        signal: Signal = loader.load(file_path)
        self.draw(signal.x_vec, signal.y_vec)

    def draw(self, x, y):
        self.pen = pg.mkPen(color=(255, 0, 0))
        self.x1, self.y1 = x, y
        self.widget.plot(self.x1, self.y1, pen=self.pen)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
