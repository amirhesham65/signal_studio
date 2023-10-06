import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
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
        # set timer for real-time plotting
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.is_plotting = False  # Flag to control real-time plotting


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

    def render_signal_to_channel(self, channel, signal):
        # Set up the initial plot
        pen = pg.mkPen(color=signal.color.value)
        curve = channel.plot(signal.x_vec, signal.y_vec, pen=pen)

        # Store the data and curve for real-time updating
        self.x_vec = signal.x_vec
        self.y_vec = signal.y_vec
        self.curve = curve
        self.data_index = 0

        # Start the real-time plot
        self.is_plotting = True
        self.timer.start(1)  # Update every 1 ms

    def update_plot(self):
       if self.is_plotting:
            if self.data_index < len(self.x_vec):
                x_data = self.x_vec[:self.data_index + 1]
                y_data = self.y_vec[:self.data_index + 1]
                self.curve.setData(x_data, y_data)
                self.data_index += 1
            else:
                self.is_plotting = False
                self.timer.stop()  # Stop the QTimer when all data is plotted untill we know what to do when finished


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
