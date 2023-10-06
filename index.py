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
        self.import_signal_ch1.triggered.connect(self.import_signal_channel_1)
        # import signal to ch2
        self.import_signal_ch2.triggered.connect(self.import_signal_channel_2)

    def import_signal_channel_1(self):
        signal: Signal = self.get_signal_from_file()
        self.render_signal_to_channel(channel=self.widget, signal=signal)
    
    def import_signal_channel_2(self):
        signal: Signal = self.get_signal_from_file()
        self.render_signal_to_channel(channel=self.widget_2, signal=signal)

    def get_signal_from_file(self):
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
        return signal

    def render_signal_to_channel(self, channel, signal: Signal) -> None:
        pen = pg.mkPen(color=signal.color.value)
        channel.plot(signal.x_vec, signal.y_vec, pen=pen)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
