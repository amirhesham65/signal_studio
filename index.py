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
            play_button = self.play_button_1,
            speed_button=self.speed_button_1,
            clear_button=self.clear_button_1,
            timer=self.timer_1,
            signals_list=self.signals_list_1,
            zoom_in_button= self.zoom_in_button_1,
            zoom_out_button= self.zoom_out_button_1,
            snap_button=self.snapshot_button_1
        )

        self.channel_2 = Channel(
            app=self, 
            plot_widget=self.widget_2,
            slider=self.channel2_slider,
            play_button = self.play_button_2,
            speed_button=self.speed_button_2,
            clear_button=self.clear_button_2,
            timer=self.timer_2,
            signals_list=self.signals_list_2,
            zoom_in_button= self.zoom_in_button_2,
            zoom_out_button= self.zoom_out_button_2,
            snap_button=self.snapshot_button_2
        )

        self.initialize_signals_slots()
        self.sync_button.clicked.connect(self.sync_channels)
        self.sync_button.setText(" Sync")
        self.sync_button.setIcon(self.sync_icon)
        self.sync_button.setIconSize(ICON_SIZE)
        # Prevent zooming and paning
        self.widget.setMouseEnabled(x=False, y=False)
        self.widget_2.setMouseEnabled(x=False, y=False)
        # hide speed buttons (real time signal)
        # self.speed_button_1.hide()
        # self.speed_button_2.hide()
        self.snapshots = []


    def initialize_signals_slots(self):
        # Channel 1
        self.import_signal_ch1.triggered.connect(self.channel_1.import_signal_channel)
        self.actionPlay_Pause.triggered.connect(self.channel_1.play_pause)
        self.hide_channel_1_chk.stateChanged.connect(self.toggle_channel_1)
        self.actionExport_signal.triggered.connect(self.export_pdf_dynamic_ch1)
        self.snapshot_button_1.clicked.connect(self.snapshot_ch_1)

        # Channel 2
        self.import_signal_ch2.triggered.connect(self.channel_2.import_signal_channel) 
        self.actionPlay_Pause_2.triggered.connect(self.channel_2.play_pause)
        self.hide_channel_2_chk.stateChanged.connect(self.toggle_channel_2)
        self.actionExport_signal_2.triggered.connect(self.export_pdf_dynamic_ch2)
        self.snapshot_button_2.clicked.connect(self.snapshot_ch_2)


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
            action3 = context_menu.addAction("Change Color")
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


    def move_signal_1(self, index):

        target_signal = self.channel_1.signals[index]

        data_x_y_pairs = set(list(zip(self.channel_1.x_data, self.channel_1.y_data)))
        deleted_x_y_pairs = set(list(zip(target_signal.x_vec, target_signal.y_vec)))
        updated_pairs = [pair for pair in data_x_y_pairs if pair not in deleted_x_y_pairs]

        updated_x_data = [pair[0] for pair in updated_pairs]
        updated_y_data = [pair[1] for pair in updated_pairs]
        self.channel_1.x_data = updated_x_data
        self.channel_1.y_data = updated_y_data

        self.channel_1.plot_widget.clear()
        self.channel_1.plot_widget.plot(updated_x_data, updated_y_data)
        self.channel_2.render_signal_to_channel(target_signal)
        # self.channel_2.signals.append(target_signal)
        # Add signals to channel list
        # item = QListWidgetItem(target_signal.title)
        # item.setBackground(QColor(*(target_signal.color.value)))
        # self.channel_2.signals_list.addItem(item)
        self.channel_1.signals.pop(index)
        self.channel_1.signals_list.takeItem(index)

    def showContextMenu_2(self, pos):
        selected_item = self.signals_list_2.itemAt(pos)

        if selected_item:
            selected_index = self.signals_list_2.row(selected_item)
            context_menu = QMenu(self)
            action1 = context_menu.addAction("Move to Channel 1")
            action2 = context_menu.addAction("Delete Signal")
            action3 = context_menu.addAction("Change Color")
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

    def move_signal_2(self, item, index):

        target_signal = self.channel_2.signals[index]

        data_x_y_pairs = set(list(zip(self.channel_1.x_data, self.channel_1.y_data)))
        deleted_x_y_pairs = set(list(zip(target_signal.x_vec, target_signal.y_vec)))
        updated_pairs = [pair for pair in data_x_y_pairs if pair not in deleted_x_y_pairs]

        updated_x_data = [pair[0] for pair in updated_pairs]
        updated_y_data = [pair[1] for pair in updated_pairs]
        self.channel_1.x_data = updated_x_data
        self.channel_1.y_data = updated_y_data

        self.channel_2.plot_widget.clear()
        self.channel_2.plot_widget.plot(updated_x_data, updated_y_data)
        self.channel_1.render_signal_to_channel(target_signal)
        self.channel_1.signals.append(target_signal)
        # Add signals to channel list
        # item = QListWidgetItem(target_signal.title)
        # item.setBackground(QColor(*(target_signal.color.value)))
        # self.channel_1.signals_list.addItem(item)
        self.channel_2.signals.pop(index)
        self.channel_2.signals_list.takeItem(index)


    def sync_channels(self):
        self.channel_1.sync = not self.channel_1.sync
        if self.channel_1.sync:
            # deactivate channel 2 contorls
            self.channel_2.play_button.hide()
            self.channel_2.clear_button.hide()
            self.channel_2.speed_button.hide()
            self.channel_2.zoom_in_button.hide()
            self.channel_2.zoom_out_button.hide()
            self.channel_2.speed_button.hide()
            self.channel_2.slider.hide()

            # trigger both channels with channel 1 controls
            #some code

            # hide play/pause & clear action menue
            self.actionPlay_Pause.setVisible(False)
            self.actionPlay_Pause_2.setVisible(False)
            self.clear_signal_ch1.setVisible(False)
            self.clear_signal_ch2.setVisible(False)
            self.sync_button.setText(" Unsync")
            self.sync_button.setIcon(self.unsync_icon)
            self.sync_button.setIconSize(ICON_SIZE)
            
            #Sync coresponding to channel 1
            self.channel_2.data_index = self.channel_1.data_index
        else:
            self.channel_2.play_button.show()
            self.channel_2.clear_button.show()
            self.channel_2.zoom_in_button.show()
            self.channel_2.zoom_out_button.show()
            self.channel_2.speed_button.show()
            self.actionPlay_Pause.setVisible(True)
            self.actionPlay_Pause_2.setVisible(True)
            self.clear_signal_ch1.setVisible(False)
            self.clear_signal_ch2.setVisible(False)
            self.sync_button.setIcon(self.sync_icon)
            self.sync_button.setIconSize(ICON_SIZE)



    def snapshot_ch_1(self):
        statistics = []
        for index in range(self.channel_1.signals_list.count()):
            mean, median, std, max_value, min_value = self.channel_1.get_stats(index)
            statistics.append(f"Signal {index+1} Statistics:")
            statistics.append(f"Mean: {mean}")
            statistics.append(f"Median: {median}")
            statistics.append(f"Standard Deviation: {std}")
            statistics.append(f"Max Value: {max_value}")
            statistics.append(f"Min Value: {min_value}")
            statistics.append("")
        img_filename = tempfile.mktemp(suffix=f"_{index}.png")
        self.widget.grab().save(img_filename, format="PNG")
        self.channel_1.snapshots.append(('Channel 1',img_filename, statistics))
        self.snapshots.append(('Channel 1',img_filename, statistics))
        
    def snapshot_ch_2(self):
        statistics = []
        for index in range(self.channel_2.signals_list.count()):
            mean, median, std, max_value, min_value = self.channel_2.get_stats(index)
            statistics.append(f"Signal {index+1} Statistics:")
            statistics.append(f"Mean: {mean}")
            statistics.append(f"Median: {median}")
            statistics.append(f"Standard Deviation: {std}")
            statistics.append(f"Max Value: {max_value}")
            statistics.append(f"Min Value: {min_value}")
            statistics.append("")
        img_filename = tempfile.mktemp(suffix=f"_{index}.png")
        self.widget.grab().save(img_filename, format="PNG")
        self.channel_2.snapshots.append(('Channel 2',img_filename, statistics))
        self.snapshots.append(('Channel 2',img_filename, statistics))
        




    def export_pdf_dynamic_ch1(self):
        #loop over snapshots in channel 1 and export them to pdf
        img_filenames = []
        combined_statistics = []
        for snapshot in self.channel_1.snapshots:
            img_filenames.append(snapshot[1])
            combined_statistics.append("<br>".join(snapshot[2]))
        

        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                /* Add your CSS styling here */
            </style>
        </head>
        <body>
            <h1>{{ channel_name }} Report</h1>
            {% for index in range(img_filenames|length) %}
                <img src="{{ img_filenames[index] }}" alt="Plot Image">
                <p>{{ combined_statistics[index] | safe }}</p>
            {% endfor %}
        </body>
        </html>
        """

        template = jinja2.Template(template_str)
        rendered_template = template.render(img_filenames=img_filenames, combined_statistics=combined_statistics, channel_name="Channel 1")

        config = pdfkit.configuration(wkhtmltopdf="wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdfkit.from_string(rendered_template, "Channel 2 Report.pdf", configuration=config, options={"enable-local-file-access": ""}) 


    def export_pdf_dynamic_ch2(self):
        #loop over snapshots in channel 2 and export them to pdf
        img_filenames = []
        combined_statistics = []
        for snapshot in self.channel_2.snapshots:
            img_filenames.append(snapshot[1])
            combined_statistics.append("<br>".join(snapshot[2]))
        

        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                /* Add your CSS styling here */
            </style>
        </head>
        <body>
            <h1>{{ channel_name }} Report</h1>
            {% for index in range(img_filenames|length) %}
                <img src="{{ img_filenames[index] }}" alt="Plot Image">
                <p>{{ combined_statistics[index] | safe }}</p>
            {% endfor %}
        </body>
        </html>
        """

        template = jinja2.Template(template_str)
        rendered_template = template.render(img_filenames=img_filenames, combined_statistics=combined_statistics, channel_name="Channel 2")

        config = pdfkit.configuration(wkhtmltopdf="wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdfkit.from_string(rendered_template, "Channel 2 Report.pdf", configuration=config, options={"enable-local-file-access": ""}) 


        def export_pdf_dynamic(self):
            channel_name = []
            img_filenames = []
            combined_statistics = []
            for snapshot in self.snapshots:
                channel_name.append(snapshot[0])
                img_filenames.append(snapshot[1])
                combined_statistics.append("<br>".join(snapshot[2]))
            

            template_str = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    /* Add your CSS styling here */
                </style>
            </head>
            <body>
                {% for index in range(img_filenames|length) %}
                    <h1>{{ channel_name }}</h1>
                    <img src="{{ img_filenames[index] }}" alt="Plot Image">
                    <p>{{ combined_statistics[index] | safe }}</p>
                {% endfor %}
            </body>
            </html>
            """

            template = jinja2.Template(template_str)
            rendered_template = template.render(img_filenames=img_filenames, combined_statistics=combined_statistics, channel_name= channel_name)

            config = pdfkit.configuration(wkhtmltopdf="wkhtmltopdf\\bin\\wkhtmltopdf.exe")
            pdfkit.from_string(rendered_template, "Report.pdf", configuration=config, options={"enable-local-file-access": ""}) 

    

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
