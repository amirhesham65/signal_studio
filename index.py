import sys
from math import floor
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import pyqtgraph as pg
from models.signal import Signal
from helpers.get_signal_from_file import get_signal_from_file

uiclass, baseclass = pg.Qt.loadUiType("main.ui")

class MainWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initialize_state()
        self.initialize_signals_slots()

        # Prevent zooming and paning
        self.widget.setMouseEnabled(x=False, y=False)
        self.widget_2.setMouseEnabled(x=False, y=False)

    def initialize_state(self):
        # Channel 1
        self.timer_1 = QTimer(self)
        self.is_plotting_1 = False
        self.speed_1 = 1

        # Channel 2
        self.timer_2 = QTimer(self)
        self.is_plotting_2 = False  
        self.speed_2 = 1 

    def initialize_signals_slots(self):
        # Channel 1
        self.import_signal_ch1.triggered.connect(self.import_signal_channel_1)
        self.timer_1.timeout.connect(self.update_plot_1)
        self.play_button_1.clicked.connect(self.play_pause_1)
        self.speed_button_1.clicked.connect(self.change_speed_1)
        self.clear_button_1.clicked.connect(self.clear_1)
        self.actionPlay_Pause.triggered.connect(self.play_pause_1)
        self.channel1_slider.valueChanged.connect(self.on_channel_1_slider_change)

        # Channel 2
        self.import_signal_ch2.triggered.connect(self.import_signal_channel_2) 
        self.timer_2.timeout.connect(self.update_plot_2)
        self.play_button_2.clicked.connect(self.play_pause_2)
        self.speed_button_2.clicked.connect(self.change_speed_2)
        self.clear_button_2.clicked.connect(self.clear_2)
        self.actionPlay_Pause_2.triggered.connect(self.play_pause_2)
        self.channel2_slider.valueChanged.connect(self.on_channel_2_slider_change)

    def on_channel_1_slider_change(self, value):
        self.widget.setXRange(value - 1, value)

    def on_channel_2_slider_change(self, value):
        self.widget_2.setXRange(value - 1, value)

    def import_signal_channel_1(self):
        signal: Signal = get_signal_from_file(self)
        if signal is not None:
            self.render_signal_to_channel_1(channel=self.widget, signal=signal)
    
    def import_signal_channel_2(self):
        signal: Signal = get_signal_from_file(self)
        if signal is not None:
            self.render_signal_to_channel_2(channel=self.widget_2, signal=signal)

    def render_signal_to_channel_1(self, channel, signal):
        # Set up the initial plot
        pen = pg.mkPen(color=signal.color.value)
        curve_1 = channel.plot(signal.x_vec, signal.y_vec, pen=pen)

        # Store the data and curve for real-time updating
        self.x_vec_1 = signal.x_vec
        self.y_vec_1 = signal.y_vec
        self.curve_1 = curve_1
        self.data_index_1 = 0

        # Fix the y-limit (prevent auto vertical zooming)
        y_limit_min, y_limit_max = curve_1.dataBounds(1)
        self.widget.setYRange(y_limit_min, y_limit_max)

        # Initialize the slider with the right values
        _, x_limit_max = curve_1.dataBounds(0)
        self.channel1_slider.setMinimum(1)
        self.channel1_slider.setMaximum(int(x_limit_max))

    def render_signal_to_channel_2(self, channel, signal):
        # Set up the initial plot
        pen = pg.mkPen(color=signal.color.value)
        curve_2 = channel.plot(signal.x_vec, signal.y_vec, pen=pen)

        # Store the data and curve for real-time updating
        self.x_vec_2 = signal.x_vec
        self.y_vec_2 = signal.y_vec
        self.curve_2 = curve_2
        self.data_index_2 = 0

        # Fix the y-limit (prevent auto vertical zooming)
        y_limit_min, y_limit_max = curve_2.dataBounds(1)
        self.widget_2.setYRange(y_limit_min, y_limit_max)

        # Initialize the slider with the right values
        _, x_limit_max = curve_2.dataBounds(0)
        self.channel2_slider.setMinimum(1)
        self.channel2_slider.setMaximum(int(x_limit_max))

    def update_plot_1(self):
       if self.is_plotting_1:
            if self.data_index_1 < len(self.x_vec_1):
                x_data = self.x_vec_1[:self.data_index_1 + 1]
                y_data = self.y_vec_1[:self.data_index_1 + 1]
                if(x_data[-1] < 1):
                    self.widget.setXRange(0, 1)
                else:    
                    self.widget.setXRange(x_data[-1]-1, x_data[-1])
                self.channel1_slider.setValue(int(x_data[-1]))
                self.channel1_slider.repaint()
                self.curve_1.setData(x_data, y_data)
                self.data_index_1 += 1     
            else:
                self.is_plotting_1 = False
                self.timer_1.stop()  # Stop the QTimer when all data is plotted untill we know what to do when finished
                self.play_button_1.setText('Rewind')

    def update_plot_2(self):
       if self.is_plotting_2:
            if self.data_index_2 < len(self.x_vec_2):
                x_data = self.x_vec_2[:self.data_index_2 + 1]
                y_data = self.y_vec_2[:self.data_index_2 + 1]
                if(x_data[-1] < 1):
                    self.widget_2.setXRange(0, 1)
                else:    
                    self.widget_2.setXRange(x_data[-1]-1, x_data[-1])
                self.channel2_slider.setValue(int(x_data[-1]))
                self.channel2_slider.repaint()
                self.curve_2.setData(x_data, y_data)
                self.data_index_2 += 1
            else:
                self.is_plotting_2 = False
                self.timer_2.stop()  # Stop the QTimer when all data is plotted untill we know what to do when finished
                self.play_button_2.setText('Rewind')
        
    def play_pause_1(self):
        if(self.data_index_1 >= len(self.x_vec_1)):
           self.data_index_1 = 0
           self.is_plotting_1 = True
           self.timer_1.start(floor( 8/self.speed_1))  # Update every 1 ms
           self.play_button_1.setText('Pause')    
        elif(self.is_plotting_1):
           self.is_plotting_1 = False
           self.timer_1.stop()  # Update every 1 ms
           self.play_button_1.setText('Play')
        else:
           self.is_plotting_1 = True
           self.timer_1.start(floor( 8/self.speed_1))  # Update every 1 ms
           self.play_button_1.setText('Pause')    

    def change_speed_1(self):
        if(self.speed_1 == 8):
            self.speed_1 = 1
            self.timer_1.start(floor( 8/self.speed_1))
            self.speed_button_1.setText(str(self.speed_1) + 'x')   
        else:
            self.speed_1 *= 2
            self.timer_1.start(floor( 8/self.speed_1))
            self.speed_button_1.setText(str(self.speed_1) + 'x')  

    def play_pause_2(self):
        if(self.data_index_2 >= len(self.x_vec_2)):
           self.data_index_2 = 0
           self.is_plotting_2 = True
           self.timer_2.start(floor( 8/self.speed_2))  # Update every 1 ms
           self.play_button_2.setText('Pause')    
        elif(self.is_plotting_2):
           self.is_plotting_2 = False
           self.timer_2.stop()  # Update every 1 ms
           self.play_button_2.setText('Play')
        else:
           self.is_plotting_2 = True
           self.timer_2.start(floor( 8/self.speed_2))  # Update every 1 ms
           self.play_button_2.setText('Pause')    

    def change_speed_2(self):
        if(self.speed_2 == 8):
            self.speed_2 = 1
            self.timer_2.start(floor( 8/self.speed_2))
            self.speed_button_1.setText(str(self.speed_2) + 'x')   
        else:
            self.speed_2 *= 2
            self.timer_2.start(floor( 8/self.speed_2))
            self.speed_button_2.setText(str(self.speed_2) + 'x')  

    def clear_1(self):  
        self.widget.clear()
        self.is_plotting_1 = False
        self.timer_1.stop()  # Update every 1 ms
        self.play_button_1.setText('Play')
        # reset x, y asix
        self.on_channel_1_slider_change(1)
        self.initialize_signals_slots()
        # reset slider
        self.channel1_slider.setValue(1)

    def clear_2(self):  
        self.widget_2.clear()    
        self.is_plotting_2 = False
        self.timer_2.stop()  # Update every 1 ms
        self.play_button_2.setText('Play')
        # reset x, y asix
        self.on_channel_2_slider_change(1)
        self.initialize_signals_slots()
        # reset slider
        self.channel2_slider.setValue(1)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
