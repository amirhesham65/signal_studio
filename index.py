import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, Qt
import pyqtgraph as pg
from models.channel import Channel

uiclass, baseclass = pg.Qt.loadUiType("main.ui")

class MainWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.timer_1 = QTimer(self)
        self.timer_2 = QTimer(self)

        self.channel_1 = Channel(
            app=self, 
            plot_widget=self.widget,
            slider=self.channel1_slider,
            play_button = self.play_button_1,
            speed_button=self.speed_button_1,
            clear_button=self.clear_button_1,
            timer=self.timer_1
        )

        self.channel_2 = Channel(
            app=self, 
            plot_widget=self.widget_2,
            slider=self.channel2_slider,
            play_button = self.play_button_2,
            speed_button=self.speed_button_2,
            clear_button=self.clear_button_2,
            timer=self.timer_2
        )

        self.initialize_signals_slots()

        # Prevent zooming and paning
        self.widget.setMouseEnabled(x=False, y=False)
        self.widget_2.setMouseEnabled(x=False, y=False)

    def initialize_signals_slots(self):
        # Channel 1
        self.import_signal_ch1.triggered.connect(self.channel_1.import_signal_channel)
        self.actionPlay_Pause.triggered.connect(self.channel_1.play_pause)
        self.hide_channel_1_chk.stateChanged.connect(self.toggle_channel_1)

        # Channel 2
        self.import_signal_ch2.triggered.connect(self.channel_2.import_signal_channel) 
        self.actionPlay_Pause_2.triggered.connect(self.channel_2.play_pause)
        self.hide_channel_2_chk.stateChanged.connect(self.toggle_channel_2)
    
    def toggle_channel_1(self, state):
        self.channel_1_container.setVisible(state == 0)

    def toggle_channel_2(self, state):
        self.channel_2_container.setVisible(state == 0)



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
