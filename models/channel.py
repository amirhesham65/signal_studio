from math import floor
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QSize
import pyqtgraph as pg
from PyQt6.uic.properties import QtGui, QtCore
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
        self.sync = False
        self.curves = []
        self.data_index = 0
        # todo replace icons with more visually appealing ones, just replace each icon with it's correpsoning ones, keeping
        #  naming of each btn so the structure of the code remains unchanged.
        self.play_icon = QIcon()
        self.play_icon.addPixmap(QPixmap("./imgs/buttons_img/play_btn.png"))
        # self.play_button.setIcon(play_icon)
        # self.play_button.setIconSize(QSize(30, 30))

        self.pause_icon = QIcon()
        self.pause_icon.addPixmap(QPixmap("./imgs/buttons_img/pause_btn.png"))

        self.rewind_icon = QIcon()
        self.rewind_icon.addPixmap(QPixmap("./imgs/buttons_img/rewind_btn.png"))

        self.clear_icon = QIcon()
        self.clear_icon.addPixmap(QPixmap("./imgs/buttons_img/clear_btn.png"))

        self.zoom_in = QIcon()
        self.zoom_out = QIcon()

        self.initialize_signals_slots()

    def initialize_signals_slots(self):
        self.timer.timeout.connect(self.update_plot)
        self.play_button.setText("")
        self.play_button.setIcon(self.play_icon)
        self.play_button.setIconSize(QSize(30, 30))
        self.play_button.clicked.connect(self.play_pause)
        self.speed_button.clicked.connect(self.change_speed)
        self.clear_button.clicked.connect(self.clear)
        self.clear_button.setText("")
        self.clear_button.setIcon(self.clear_icon)
        self.clear_button.setIconSize(QSize(30, 30))
        self.slider.valueChanged.connect(self.on_channel_slider_change)





    def on_channel_slider_change(self, value):
        self.plot_widget.setXRange(value - 1, value)
        if self.sync:
            self.app.channel_2.slider.setValue(value)
            self.app.channel_2.plot_widget.setXRange(value - 1, value)
            self.app.channel_2.slider.repaint()

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
            
            signal_color_cb.addItems(["Red", "Blue", "Green", "Orange", "Yellow", "Purple"])
            dialog_layout.addWidget(signal_input)
            dialog_layout.addWidget(signal_color_cb)
            dialog_layout.addWidget(add_button)
            dialog_layout.addStretch()
            dialog.setLayout(dialog_layout)

            def add_signal():
                if signal_input.text():
                    signal.title = signal_input.text()
                signal_color = signal_color_cb.currentText()
                match signal_color:
                    case "Blue":
                        signal.color = SignalColor.BLUE
                    case "Red":
                        signal.color = SignalColor.RED
                    case "Green":
                        signal.color = SignalColor.GREEN
                    case "Yellow":
                        signal.color = SignalColor.YELLOW
                    case "Orange":
                        signal.color = SignalColor.ORANGE
                    case "Purple":
                        signal.color = SignalColor.PURPLE
                self.render_signal_to_channel(signal=signal)
                dialog.close()
            add_button.clicked.connect(add_signal)

            dialog.exec()
               

    def render_signal_to_channel(self, signal):
        # Set up the initial plot
        item = QListWidgetItem(signal.title)
        item.setBackground(QColor(*(signal.color.value)))
        self.signals_list.addItem(item)
        self.signals.append(signal)
        self.x_data.extend(signal.x_vec)
        self.y_data.extend(signal.y_vec)
        pen = pg.mkPen(color=signal.color.value)
        curve = self.plot_widget.plot(signal.x_vec, signal.y_vec, pen=pen)
        self.curves.append(curve)

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
            if self.data_index < len(self.x_data):
                x_data = self.x_data[:self.data_index + 1]
                y_data = self.y_data[:self.data_index + 1]
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
                self.play_button.setIcon(self.rewind_icon)
                self.play_button.setIconSize(QSize(30, 30))

    # def get_stats(self, index):
    #     signal = self.signals[index]
    #     print(signal.get_statistics(self.data_index))


    def play_pause(self):
        if len(self.signals_list) == 0:
            # self.play_button.setText('Play')
            self.play_button.setIcon(self.play_icon)
            self.play_button.setIconSize(QSize(30, 30))
        else:
            try:
                if(self.data_index >= len(self.x_data)):
                   self.data_index = 0
                   self.is_plotting = True
                   self.timer.start(floor(8/self.speed))  # Update every 1 ms
                   self.play_button.setIcon(self.pause_icon)
                   self.play_button.setIconSize(QSize(30, 30))
                elif(self.is_plotting):
                   self.is_plotting = False
                   self.timer.stop()  # Update every 1 ms
                   self.play_button.setIcon(self.play_icon)
                   self.play_button.setIconSize(QSize(30, 30))
                else:
                   self.is_plotting = True
                   self.timer.start(floor(8/self.speed))  # Update every 1 ms
                   self.play_button.setIcon(self.pause_icon)
                   self.play_button.setIconSize(QSize(30, 30))
            except Exception:
                QMessageBox.warning(self.app, "Warning", "Select the data first!")


        # check if synced
        if self.sync:
            self.app.channel_2.play_pause()


    def change_speed(self):
        if self.sync:
            self.app.channel_2.speed = self.speed
        if(self.speed == 8):
            self.speed = 1
            self.timer.start(floor( 8/self.speed))
            self.speed_button.setText(str(self.speed) + 'x')   
        else:
            self.speed *= 2
            self.timer.start(floor( 8/self.speed))
            self.speed_button.setText(str(self.speed) + 'x')

        # check if synced
        if self.sync:
            self.app.channel_2.change_speed()

    def clear(self):  
        self.plot_widget.clear()
        self.is_plotting = False
        self.timer.stop()  # Update every 1 ms
        self.play_button.setIcon(self.play_icon)
        self.play_button.setIconSize(QSize(30, 30))
        # reset x, y asix
        self.on_channel_slider_change(1)
        # self.initialize_signals_slots()
        # reset slider
        self.slider.setValue(0)
        # clear signal list
        self.signals_list.clear()
        self.x_data = []
        self.y_data = []
        self.data_index = 0
        
         # check if synced
        if self.sync:
            self.app.channel_2.clear()


    def remove_signal(self, index):

        data_x_y_pairs = set(list(zip(self.x_data, self.y_data)))
        deleted_x_y_pairs = set(list(zip(self.signals[index].x_vec, self.signals[index].y_vec)))
        updated_pairs = [pair for pair in data_x_y_pairs if pair not in deleted_x_y_pairs]

        updated_x_data = [pair[0] for pair in updated_pairs]
        updated_y_data = [pair[1] for pair in updated_pairs]
        self.x_data = updated_x_data
        self.y_data = updated_y_data
        
        self.plot_widget.clear()
        self.plot_widget.plot(updated_x_data, updated_y_data)
        self.signals.pop(index)
        self.signals_list.takeItem(index)

    def hide_unhide(self, index):
        signal = self.signals[index];
        signal.hidden = not signal.hidden
        def hide_signal(signal):
            self.signals_list.setCurrentRow(index)
            item = self.signals_list.currentItem()
            item.setBackground(QColor(*signal.color.value + (128,)))
            signal.last_drawn_index = self.data_index
            pen = pg.mkPen(color=SignalColor.TRANSPARENT.value)
            self.curve = self.plot_widget.plot(signal.x_vec, signal.y_vec, pen=pen)

        def unhide_signal(signal):
            self.signals_list.setCurrentRow(index)
            item = self.signals_list.currentItem()
            item.setBackground(QColor(*signal.color.value))
            pen = pg.mkPen(color=signal.color.value)
            if signal.last_drawn_index == 0:
                self.curve = self.plot_widget.plot(signal.x_vec, signal.y_vec, pen=pen)
            else:
                self.curve = self.plot_widget.plot(signal.x_vec[:self.data_index], signal.y_vec[:self.data_index], pen=pen)

        if signal.hidden:
            hide_signal(signal)
        else:
            unhide_signal(signal)

    def change_color(self, index, color):
        signal = self.signals[index]
        self.signals_list.setCurrentRow(index)
        item = self.signals_list.currentItem()
        item.setBackground(QColor(*(color.value)))
        pen = pg.mkPen(color=signal.color.value)
        if signal.last_drawn_index == 0:
            self.curve = self.plot_widget.plot(signal.x_vec, signal.y_vec, pen=pen)
        else:
            self.curve = self.plot_widget.plot(signal.x_vec[:self.data_index], signal.y_vec[:self.data_index], pen=pen)

    def edit_signal(self, index):
            signal = self.signals[index];
            dialog = QDialog(self.app)
            dialog.resize(400, 100)

            # Building the dialog content
            dialog_layout = QVBoxLayout()
            signal_input = QLineEdit()
            signal_input.setText(signal.title)
            signal_color_cb = QComboBox()
            add_button = QPushButton("Edit Signal")
            
            signal_color_cb.addItems(["Red", "Blue", "Green", "Orange", "Yellow", "Purple"])

            dialog_layout.addWidget(signal_input)
            dialog_layout.addWidget(signal_color_cb)
            dialog_layout.addWidget(add_button)
            dialog_layout.addStretch()
            dialog.setLayout(dialog_layout)

            def edit():
                if signal_input.text():
                    signal.title = signal_input.text()
                signal_color = signal_color_cb.currentText()
                match signal_color:
                    case "Blue":
                        signal.color = SignalColor.BLUE
                    case "Red":
                        signal.color = SignalColor.RED
                    case "Green":
                        signal.color = SignalColor.GREEN
                    case "Yellow":
                        signal.color = SignalColor.YELLOW
                    case "Orange":
                        signal.color = SignalColor.ORANGE
                    case "Purple":
                        signal.color = SignalColor.PURPLE
                self.change_color(index, signal.color)
                dialog.close()
            add_button.clicked.connect(edit)

            dialog.exec()   

