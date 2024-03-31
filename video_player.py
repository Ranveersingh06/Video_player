import sys
import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QSlider, QMainWindow, QAction, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.video_capture = cv2.VideoCapture(0)  # Open default camera
        self.is_playing = False

        self.image_label = QLabel()

        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.clicked.connect(self.toggle_playback)

        self.grayscale_button = QPushButton("Grayscale")
        self.grayscale_button.clicked.connect(self.toggle_grayscale)

       

        layout = QVBoxLayout()
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.start_stop_button)
        control_layout.addWidget(self.grayscale_button)
        layout.addWidget(self.image_label)
        layout.addLayout(control_layout)
      
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_frame)
        self.timer.start(1000 // 30)  # 30 FPS

    def toggle_playback(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.start_stop_button.setText("Stop")
        else:
            self.start_stop_button.setText("Start")

    def toggle_grayscale(self):
        ret, frame = self.video_capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            h, w = frame.shape
            bytes_per_line = w
            convert_to_Qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
            p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
            self.image_label.setPixmap(QPixmap.fromImage(p))

    
    def display_frame(self):
        if self.is_playing:
            ret, frame = self.video_capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
                self.image_label.setPixmap(QPixmap.fromImage(p))

    def closeEvent(self, event):
        self.video_capture.release()
        event.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Player")

        self.video_player = VideoPlayer()
        self.setCentralWidget(self.video_player)

        self.create_menu()
        self.create_toolbar()

    def create_menu(self):
        open_file_action = QAction("Open Video File", self)
        open_file_action.triggered.connect(self.open_file)
        
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(open_file_action)

    def create_toolbar(self):
        toolbar = self.addToolBar("Controls")

        start_action = QAction("Start", self)
        start_action.triggered.connect(self.video_player.toggle_playback)
        toolbar.addAction(start_action)

        grayscale_action = QAction("Grayscale", self)
        grayscale_action.triggered.connect(self.video_player.toggle_grayscale)
        toolbar.addAction(grayscale_action)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi)")
        if file_name:
            self.video_player.video_capture.release()
            self.video_player.video_capture = cv2.VideoCapture(file_name)
            self.video_player.is_playing = True
            self.video_player.start_stop_button.setText("Stop")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
