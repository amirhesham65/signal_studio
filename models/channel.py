from math import floor
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from models.signal import Signal, SignalColor
from helpers.get_signal_from_file import get_signal_from_file

class Channel:
    def __init__(self, app, plot_widget, slider, play_button, speed_button, clear_button, timer, signals_list) -> None:
        self.app = app
        self.is_plotting = False
        self.speed = 1
        self.y_min = None
        self.y_max = None
        
        self.plot_widget = plot_widget
        self.slider = slider
        self.play_button = play_button
        self.speed_button = speed_button
        self.clear_button = clear_button
        self.timer = timer
        self.signals_list = signals_list
        self.signals = []
        self.x_data = []
        self.y_data = []

        self.initialize_signals_slots()

    def initialize_signals_slots(self):
        self.timer.timeout.connect(self.update_plot)
        self.play_button.clicked.connect(self.play_pause)
        self.speed_button.clicked.connect(self.change_speed)
        self.clear_button.clicked.connect(self.clear)
        self.slider.valueChanged.connect(self.on_channel_slider_change)
    
    def on_channel_slider_change(self, value):
        self.plot_widget.setXRange(value - 1, value)

    def import_signal_channel(self):
        signal: Signal = get_signal_from_file(self.app)

        if signal is not None:
            dialog = QDialog(self.app)
            dialog.resize(400, 100)

            # Building the dialog content
            dialog_layout = QVBoxLayout()
            signal_input = QLineEdit()
            signal_color_cb = QComboBox()
            add_button = QPushButton("Add Signal")
            
            signal_color_cb.addItems(["White", "Red", "Blue"])
            dialog_layout.addWidget(signal_input)
            dialog_layout.addWidget(signal_color_cb)
            dialog_layout.addWidget(add_button)
            dialog_layout.addStretch()
            dialog.setLayout(dialog_layout)

            def add_signal():
                if signal_input.text():
                    signal.title = signal_input.text()
                if signal_color_cb.currentText() == "Blue":
                    signal.color = SignalColor.BLUE
                elif signal_color_cb.currentText() == "Red":
                    signal.color = SignalColor.RED
                else:
                    signal.color = SignalColor.GREEN
                print(signal_color_cb.currentText())
                item = QListWidgetItem(signal.title)
                item.setBackground(QColor(*(signal.color.value)))
                self.render_signal_to_channel(signal=signal)
                self.signals_list.addItem(item)
                self.signals.append(signal)
                if len(self.signals_list) != 0:
                    self.x_data.extend(signal.x_vec)
                    self.y_data.extend(signal.y_vec)
                dialog.close()
            add_button.clicked.connect(add_signal)

            dialog.exec()
               

    def render_signal_to_channel(self, signal):
        # Set up the initial plot
        pen = pg.mkPen(color=signal.color.value)
        curve = self.plot_widget.plot(signal.x_vec, signal.y_vec, pen=pen)

        # Store the data and curve for real-time updating
        self.x_vec = signal.x_vec
        self.y_vec = signal.y_vec
        self.curve = curve
        self.data_index = 0

        # Fix the y-limit (prevent auto vertical zooming)
        y_limit_min, y_limit_max = curve.dataBounds(1)
        if self.y_min is None and self.y_max is None:
            self.y_min = y_limit_min
            self.y_max = y_limit_max
        else:
            self.y_min = min(self.y_min, y_limit_min)
            self.y_max = max(self.y_max, y_limit_max)
        self.plot_widget.setYRange(self.y_min, self.y_max)

        # Initialize the slider with the right values
        _, x_limit_max = curve.dataBounds(0)
        self.slider.setMinimum(1)
        self.slider.setMaximum(int(x_limit_max))
    
    def update_plot(self):
       if self.is_plotting:
            if self.data_index < len(self.x_vec):
                x_data = self.x_vec[:self.data_index + 1]
                y_data = self.y_vec[:self.data_index + 1]
                if(x_data[-1] < 1):
                    self.plot_widget.setXRange(0, 1)
                else:    
                    self.plot_widget.setXRange(x_data[-1]-1, x_data[-1])
                self.slider.setValue(int(x_data[-1]))
                self.slider.repaint()
                self.curve.setData(x_data, y_data)
                self.data_index += 1     
            else:
                self.is_plotting = False
                self.timer.stop() 
                self.play_button.setText('Rewind')

    def play_pause(self):
        if len(self.signals_list) == 0:
            self.play_button.setText('Play')
        else:
            try:
                if(self.data_index >= len(self.x_vec)):
                   self.data_index = 0
                   self.is_plotting = True
                   self.timer.start(floor(8/self.speed))  # Update every 1 ms
                   self.play_button.setText('Pause')
                elif(self.is_plotting):
                   self.is_plotting = False
                   self.timer.stop()  # Update every 1 ms
                   self.play_button.setText('Play')
                else:
                   self.is_plotting = True
                   self.timer.start(floor(8/self.speed))  # Update every 1 ms
                   self.play_button.setText('Pause')
            except Exception:
                QMessageBox.warning(self.app, "Warning", "Select the data first!")


        # if self.app.sync:  Recurssion Error
        #     self.app.channel_2.play_pause()

    def change_speed(self):
        if(self.speed == 8):
            self.speed = 1
            self.timer.start(floor( 8/self.speed))
            self.speed_button.setText(str(self.speed) + 'x')   
        else:
            self.speed *= 2
            self.timer.start(floor( 8/self.speed))
            self.speed_button.setText(str(self.speed) + 'x')

        # # check if synced
        # if self.app.sync:
        #     self.app.channel_2.change_speed()

    def clear(self):  
        self.plot_widget.clear()
        self.is_plotting = False
        self.timer.stop()  # Update every 1 ms
        self.play_button.setText('Play')
        # reset x, y asix
        self.on_channel_slider_change(1)
        # self.initialize_signals_slots()
        # reset slider
        self.slider.setValue(0)
        # clear signal list
        self.signals_list.clear()


    def remove_signal(self, index):
        updated_x_data = []
        updated_y_data = []
        for x, y in zip(self.x_data, self.y_data):
            if x not in self.signals[index].x_vec and y not in self.signals[index].y_vec:
                updated_x_data.append(x)
                updated_y_data.append(y)

        self.plot_widget.clear()
        self.plot_widget.plot(updated_x_data, updated_y_data)
        self.signals.pop(index)
        self.signals_list.takeItem(index)
        

