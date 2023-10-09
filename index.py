import sys
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
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

        self.signals_list_1.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.signals_list_1.customContextMenuRequested.connect(self.showContextMenu_1)

        self.signals_list_2.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.signals_list_2.customContextMenuRequested.connect(self.showContextMenu_2)

        self.channel_1 = Channel(
            app=self, 
            plot_widget=self.widget,
            slider=self.channel1_slider,
            play_button = self.play_button_1,
            speed_button=self.speed_button_1,
            clear_button=self.clear_button_1,
            timer=self.timer_1,
            signals_list=self.signals_list_1
        )

        self.channel_2 = Channel(
            app=self, 
            plot_widget=self.widget_2,
            slider=self.channel2_slider,
            play_button = self.play_button_2,
            speed_button=self.speed_button_2,
            clear_button=self.clear_button_2,
            timer=self.timer_2,
            signals_list=self.signals_list_2
        )

        self.initialize_signals_slots()
        self.sync_button.clicked.connect(self.sync_channels)
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

    def showContextMenu_1(self, pos):
        selected_item = self.signals_list_1.itemAt(pos)
        
        if selected_item:
            selected_index = self.signals_list_1.row(selected_item)
            context_menu = QMenu(self)
            action1 = context_menu.addAction("Move to Channel 2")
            action2 = context_menu.addAction("Delete Signal")
            action = context_menu.exec(QCursor.pos())
            if action == action1:
                self.item_menu_1(selected_item, selected_index)
            if action == action2:
                self.channel_1.remove_signal(selected_index)
            # clear channel if it displays no signals
            if len(self.channel_1.signals_list) == 0:
                self.channel_1.clear()

    def item_menu_1(self, item, index):
        updated_x_data = []
        updated_y_data = []

        target_signal = self.channel_1.signals[index]

        for x, y in zip(self.channel_1.x_data, self.channel_1.y_data):
            if x not in target_signal.x_vec and y not in target_signal.y_vec:
                updated_x_data.append(x)
                updated_y_data.append(y)

        self.channel_1.plot_widget.clear()
        self.channel_1.plot_widget.plot(updated_x_data, updated_y_data)
        self.channel_2.render_signal_to_channel(target_signal)
        self.channel_2.signals.append(target_signal)
        # Add signals to channel list
        item = QListWidgetItem(target_signal.title)
        item.setBackground(QColor(*(target_signal.color.value)))
        self.channel_2.signals_list.addItem(item)
        self.channel_1.signals.pop(index)
        self.channel_1.signals_list.takeItem(index)

    def showContextMenu_2(self, pos):
        selected_item = self.signals_list_2.itemAt(pos)

        if selected_item:
            selected_index = self.signals_list_2.row(selected_item)
            context_menu = QMenu(self)
            action1 = context_menu.addAction("Move to Channel 1")
            action2 = context_menu.addAction("Delete Signal")
            action = context_menu.exec(QCursor.pos())
            if action == action1:
                self.item_menu_2(selected_item, selected_index)

            if action == action2:
                self.channel_2.remove_signal(selected_index)
            if len(self.channel_2.signals_list) == 0:
                self.channel_2.clear()

    def item_menu_2(self, item, index):

        updated_x_data = []
        updated_y_data = []

        target_signal = self.channel_2.signals[index]

        for x, y in zip(self.channel_2.x_data, self.channel_2.y_data):
            if x not in target_signal.x_vec and y not in target_signal.y_vec:
                updated_x_data.append(x)
                updated_y_data.append(y)

        self.channel_2.plot_widget.clear()
        self.channel_2.plot_widget.plot(updated_x_data, updated_y_data)
        self.channel_1.render_signal_to_channel(target_signal)
        self.channel_1.signals.append(target_signal)
        # Add signals to channel list
        item = QListWidgetItem(target_signal.title)
        item.setBackground(QColor(*(target_signal.color.value)))
        self.channel_1.signals_list.addItem(item)
        self.channel_2.signals.pop(index)
        self.channel_2.signals_list.takeItem(index)


    def sync_channels(self):
        self.channel_1.sync = not self.channel_1.sync
        if self.channel_1.sync:
            # deactivate channel 2 contorls
            self.channel_2.play_button.hide()
            self.channel_2.clear_button.hide()
            self.channel_2.speed_button.hide()

            # trigger both channels with channel 1 controls
            #some code

            # hide play/pause & clear action menue
            self.actionPlay_Pause.setVisible(False)
            self.actionPlay_Pause_2.setVisible(False)
            self.clear_signal_ch1.setVisible(False)
            self.clear_signal_ch2.setVisible(False)
            self.sync_button.setText("Unsync")
        else:
            self.channel_2.play_button.show()
            self.channel_2.clear_button.show()
            self.channel_2.speed_button.show()
            self.actionPlay_Pause.setVisible(True)
            self.actionPlay_Pause_2.setVisible(True)
            self.clear_signal_ch1.setVisible(False)
            self.clear_signal_ch2.setVisible(False)
            self.sync_button.setText("Sync")
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
