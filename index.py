import sys
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer, Qt, QSize
import pyqtgraph as pg
from models.channel import Channel, ICON_SIZE
import pdfkit
import jinja2
from io import BytesIO
import tempfile

uiclass, baseclass = pg.Qt.loadUiType("main.ui")


class MainWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Signal Studio")

        self.timer_1 = QTimer(self)
        self.timer_2 = QTimer(self)

        self.signals_list_1.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.signals_list_1.customContextMenuRequested.connect(self.showContextMenu_1)

        self.signals_list_2.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.signals_list_2.customContextMenuRequested.connect(self.showContextMenu_2)

        self.sync_icon = QIcon()
        self.sync_icon.addPixmap(QPixmap("./imgs/buttons_img/sync_btn.png"))

        self.unsync_icon = QIcon()
        self.unsync_icon.addPixmap(QPixmap("./imgs/buttons_img/unsync_btn.png"))

        self.channel_1 = Channel(
            app=self,
            plot_widget=self.widget,
            slider=self.channel1_slider,
            play_button=self.play_button_1,
            speed_button=self.speed_button_1,
            clear_button=self.clear_signal_ch1,
            timer=self.timer_1,
            signals_list=self.signals_list_1,
            zoom_in_button=self.zoom_in_button_1,
            zoom_out_button=self.zoom_out_button_1,
            snap_button=self.snapshot_button_1,
        )

        self.channel_2 = Channel(
            app=self,
            plot_widget=self.widget_2,
            slider=self.channel2_slider,
            play_button=self.play_button_2,
            speed_button=self.speed_button_2,
            clear_button=self.clear_signal_ch2,
            timer=self.timer_2,
            signals_list=self.signals_list_2,
            zoom_in_button=self.zoom_in_button_2,
            zoom_out_button=self.zoom_out_button_2,
            snap_button=self.snapshot_button_2,
        )

        self.initialize_signals_slots()
        self.sync_button.clicked.connect(self.sync_channels)
        self.sync_button.setText(" Sync")
        self.sync_button.setIcon(self.sync_icon)
        self.sync_button.setIconSize(ICON_SIZE)
        # # Prevent zooming and paning
        # self.widget.setMouseEnabled(x=False, y=False)
        # self.widget_2.setMouseEnabled(x=False, y=False)
        # hide speed buttons (real time signal)
        # self.speed_button_1.hide()
        # self.speed_button_2.hide()
        self.snapshots = []

    def initialize_signals_slots(self):
        # Channel 1
        self.import_signal_ch1.triggered.connect(self.channel_1.import_signal_channel)
        self.actionPlay_Pause.triggered.connect(self.channel_1.play_pause)
        self.hide_channel_1_chk.stateChanged.connect(self.toggle_channel_1)
        self.snapshot_button_1.clicked.connect(self.snapshot_ch_1)

        # Channel 2
        self.import_signal_ch2.triggered.connect(self.channel_2.import_signal_channel)
        self.actionPlay_Pause_2.triggered.connect(self.channel_2.play_pause)
        self.hide_channel_2_chk.stateChanged.connect(self.toggle_channel_2)
        self.snapshot_button_2.clicked.connect(self.snapshot_ch_2)

        # Report Generation
        self.generate_Report.triggered.connect(self.export_pdf_dynamic)
        self.actionClear_Snapshots.triggered.connect(self.clear_snapshots)

    # Logic to hide channels
    def toggle_channel_1(self, state):
        self.channel_1_container.setVisible(state == 0)

    def toggle_channel_2(self, state):
        self.channel_2_container.setVisible(state == 0)

    # Channels context menu
    def showContextMenu_1(self, pos):
        selected_item = self.signals_list_1.itemAt(pos)

        if selected_item:
            selected_index = self.signals_list_1.row(selected_item)
            context_menu = QMenu(self)
            action1 = context_menu.addAction("Move to Channel 2")
            action2 = context_menu.addAction("Delete Signal")
            action3 = context_menu.addAction("Edit Signal")
            action4 = context_menu.addAction("Hide / UnHide")
            action = context_menu.exec(QCursor.pos())
            if action == action1:
                self.move_signal_1(selected_index)
            if action == action2:
                self.channel_1.remove_signal(selected_index)
            if action == action3:
                self.channel_1.edit_signal(selected_index)
            if action == action4:
                self.channel_1.hide_unhide(selected_index)
            # clear channel if it displays no signals
            if len(self.channel_1.signals_list) == 0:
                self.channel_1.clear()

    def showContextMenu_2(self, pos):
        selected_item = self.signals_list_2.itemAt(pos)

        if selected_item:
            selected_index = self.signals_list_2.row(selected_item)
            context_menu = QMenu(self)
            action1 = context_menu.addAction("Move to Channel 1")
            action2 = context_menu.addAction("Delete Signal")
            action3 = context_menu.addAction("Edit Signal")
            action4 = context_menu.addAction("Hide / UnHide")
            action = context_menu.exec(QCursor.pos())
            if action == action1:
                self.move_signal_2(selected_item, selected_index)
            if action == action2:
                self.channel_2.remove_signal(selected_index)
            if action == action3:
                self.channel_2.edit_signal(selected_index)
            if action == action4:
                self.channel_2.hide_signal(selected_index)
            if len(self.channel_2.signals_list) == 0:
                self.channel_2.clear()

    def move_signal_1(self, index):
        self.channel_2.render_signal_to_channel(self.channel_1.signals[index])
        self.channel_1.remove_signal(index)

    def move_signal_2(self, index):
        self.channel_1.render_signal_to_channel(self.channel_1.signals[index])
        self.channel_2.remove_signal(index)

    def sync_channels(self):
        self.channel_1.sync = not self.channel_1.sync
        if self.channel_1.sync:
            # deactivate channel 2 contorls
            self.channel_2.play_button.hide()
            # self.channel_2.clear_button.hide()
            self.channel_2.speed_button.hide()
            self.channel_2.zoom_in_button.hide()
            self.channel_2.zoom_out_button.hide()
            self.channel_2.speed_button.hide()
            self.channel_2.slider.hide()

            # trigger both channels with channel 1 controls
            # some code

            # hide play/pause & clear action menue
            self.actionPlay_Pause.setVisible(False)
            self.actionPlay_Pause_2.setVisible(False)
            self.clear_signal_ch1.setVisible(False)
            self.clear_signal_ch2.setVisible(False)
            self.sync_button.setText(" Unsync")
            self.sync_button.setIcon(self.unsync_icon)
            self.sync_button.setIconSize(ICON_SIZE)

            # Sync coresponding to channel 1
            self.channel_2.data_index = self.channel_1.data_index
        else:
            self.channel_2.play_button.show()
            # self.channel_2.clear_button.show()
            self.channel_2.zoom_in_button.show()
            self.channel_2.zoom_out_button.show()
            self.channel_2.speed_button.show()
            self.actionPlay_Pause.setVisible(True)
            self.actionPlay_Pause_2.setVisible(True)
            self.clear_signal_ch1.setVisible(False)
            self.clear_signal_ch2.setVisible(False)
            self.sync_button.setText(" Sync")
            self.sync_button.setIcon(self.sync_icon)
            self.sync_button.setIconSize(ICON_SIZE)

    def snapshot_ch_1(self):
        statistics = []
        for index in range(self.channel_1.signals_list.count()):
            mean, median, std, max_value, min_value = self.channel_1.get_stats(index)
            statistics.append([self.channel_1.signals[index].title,mean,median,std,max_value,min_value])
            
        img_filename = tempfile.mktemp(suffix=f"_{index}.png")
        self.widget.grab().save(img_filename, format="PNG")
        self.channel_1.snapshots.append(("Channel 1", img_filename, statistics))
        self.snapshots.append(("Channel 1", img_filename, statistics))

    def snapshot_ch_2(self):
        statistics = []
        for index in range(self.channel_2.signals_list.count()):
            mean, median, std, max_value, min_value = self.channel_2.get_stats(index)
            statistics.append([self.channel_2.signals[index].title,mean,median,std,max_value,min_value])
            

        img_filename = tempfile.mktemp(suffix=f"_{index}.png")
        self.widget_2.grab().save(img_filename, format="PNG")
        self.channel_2.snapshots.append(("Channel 2", img_filename, statistics))
        self.snapshots.append(("Channel 2", img_filename, statistics))

    def export_pdf_dynamic(self):
        channel_name = []
        img_filenames = []
        combined_statistics = []
        for snapshot in self.snapshots:
            channel_name.append(snapshot[0])
            img_filenames.append(snapshot[1])
            snapshot_statistics = []
            for index, stats in enumerate(snapshot[2]):
                snapshot_statistics.append([stats[0], stats[1], stats[2], stats[3], stats[4] , stats[5]])
            combined_statistics.append(snapshot_statistics)

        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    margin: 20px;
                }
                table {
                    display: flex;
                    flex-direction: row;
                    border-collapse: collapse;
                    border: 2px solid black;
                    margin: 10px 0;
                }
                td {
                    padding: 10px;
                    border: 1px solid black;
                }
                th {
                    padding: 10px;
                    border: 1px solid black;
                }
            </style>
        </head>
        <body>
            {% for index in range(img_filenames|length) %}
                <div class="container">
                    <h1>{{ channel_name[index] }}</h1>
                    <img src="{{ img_filenames[index] }}" alt="Plot Image">
                    <table>
                        <tr>
                            <th>Signal</th>
                            <th>Mean</th>
                            <th>Median</th>
                            <th>Standard Deviation</th>
                            <th>Minimum Value</th>
                            <th>Maximum Value</th>
                        </tr>
                        {% for stat in combined_statistics[index] %}
                            <tr>
                                <td>{{ stat[0] }}</td>
                                <td>{{ stat[1] }}</td>
                                <td>{{ stat[2] }}</td>
                                <td>{{ stat[3] }}</td>
                                <td>{{ stat[4] }}</td>
                                <td>{{ stat[5] }}</td>
                            </tr>
                        {% endfor %}
                    </table>
                </div>
                <br> <!-- Add a line break after each container -->
            {% endfor %}
        </body>
        </html>
        """

        template = jinja2.Template(template_str)
        rendered_template = template.render(
            img_filenames=img_filenames,
            combined_statistics=combined_statistics,
            channel_name=channel_name,
        )
        config = pdfkit.configuration(wkhtmltopdf="wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdfkit.from_string(
            rendered_template,
            "Report.pdf",
            configuration=config,
            options={"enable-local-file-access": ""},
        )

    def clear_snapshots(self):
        self.snapshots = []
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
