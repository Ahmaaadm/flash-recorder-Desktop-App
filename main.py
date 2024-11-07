import sys
import numpy as np
import cv2
import pyautogui
import datetime
import threading
import time
import os
import sounddevice as sd
import wave
import tempfile
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QComboBox,
    QCheckBox,
    QGridLayout
)
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt
from moviepy.editor import VideoFileClip, AudioFileClip

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        # Create the folder to store recordings if it doesn't exist
        user_videos_dir = os.path.expanduser("~\\Videos")
        self.recording_folder = os.path.join(user_videos_dir, "FlachRecRecords")

        if not os.path.exists(self.recording_folder):
            os.makedirs(self.recording_folder)

        # Set window title and size
        self.setWindowTitle('FlachRec')
        self.setFixedSize(450, 700)

        # Set background image
        oImage = QPixmap("backk.jpg")
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(oImage))
        self.setPalette(palette)

        # Create the main layout
        main_layout = QGridLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Recording icon
        self.rec_icon = QLabel(self)
        self.rec_icon.setPixmap(QPixmap("recIcon.png").scaled(30, 30, Qt.KeepAspectRatio))
        self.rec_icon.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.rec_icon.setFixedSize(50, 50)
        self.rec_icon.hide()

        main_layout.addWidget(self.rec_icon, 0, 1, alignment=Qt.AlignRight | Qt.AlignTop)

        # Tricky sentence
        tricky_sentence = QLabel("Record your screen \n effortlessly!")
        tricky_sentence.setStyleSheet(
            "font-size: 26px; color: #ffffff; text-align: center; font-family: 'Courier New';"
        )
        tricky_sentence.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(tricky_sentence, 0, 0, 1, 2, alignment=Qt.AlignCenter)

        # Frame rate selection layout
        self.fps_layout = QHBoxLayout()
        self.fps_label = QLabel("Frame Rate (fps):")
        self.fps_label.setStyleSheet("font-size: 16px; color: #ffffff; font-family: 'Courier New';")
        self.fps_combobox = QComboBox()
        self.fps_combobox.setStyleSheet(
            "font-size: 14px; padding: 5px; font-family: 'Courier New'; color: #333333;"
            "background-color: #eeeeee; border-radius: 5px;"
        )
        self.fps_combobox.addItems(["15", "30", "60"])
        self.fps_layout.addWidget(self.fps_label)
        self.fps_layout.addWidget(self.fps_combobox)
        main_layout.addLayout(self.fps_layout, 1, 0, 1, 2)

        # Output format selection layout
        self.format_layout = QHBoxLayout()
        self.format_label = QLabel("Output Format:")
        self.format_label.setStyleSheet("font-size: 16px; color: #ffffff; font-family: 'Courier New'; margin-top: 10px;")
        self.format_combobox = QComboBox()
        self.format_combobox.setStyleSheet(
            "font-size: 14px; padding: 5px; font-family: 'Courier New'; color: #333333;"
            "background-color: #eeeeee; border-radius: 5px;"
        )
        self.format_combobox.addItems(["mp4", "avi", "mkv"])
        self.format_layout.addWidget(self.format_label)
        self.format_layout.addWidget(self.format_combobox)
        main_layout.addLayout(self.format_layout, 2, 0, 1, 2)

        # Checkboxes
        checkbox_style = "font-size: 16px; color: #ffffff; font-family: 'Courier New'; margin-top: 10px;"
        self.audio_checkbox = QCheckBox("Record Audio")
        self.audio_checkbox.setStyleSheet(checkbox_style)
        main_layout.addWidget(self.audio_checkbox, 3, 0, 1, 2)

        self.countdown_checkbox = QCheckBox("Enable Countdown Timer")
        self.countdown_checkbox.setStyleSheet(checkbox_style)
        main_layout.addWidget(self.countdown_checkbox, 4, 0, 1, 2)

        self.timestamp_checkbox = QCheckBox("Overlay Timestamp")
        self.timestamp_checkbox.setStyleSheet(checkbox_style)
        main_layout.addWidget(self.timestamp_checkbox, 5, 0, 1, 2)

        # Buttons
        button_style = (
            "font-size: 18px; padding: 10px 20px; font-family: 'Arial'; color: #ffffff; "
            "background-color: #007acc; border-radius: 10px;"
        )

        self.start_button = QPushButton("Start Recording")
        self.start_button.setStyleSheet(button_style)
        self.start_button.clicked.connect(self.start_recording)
        main_layout.addWidget(self.start_button, 6, 0, 1, 2, alignment=Qt.AlignCenter)

        self.pause_stop_layout = QHBoxLayout()

        self.pause_button = QPushButton("Pause")
        self.pause_button.setStyleSheet(button_style)
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_stop_layout.addWidget(self.pause_button)
        self.pause_button.hide()

        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet(button_style)
        self.stop_button.clicked.connect(self.stop_recording)
        self.pause_stop_layout.addWidget(self.stop_button)
        self.stop_button.hide()

        main_layout.addLayout(self.pause_stop_layout, 7, 0, 1, 2)

        self.setLayout(main_layout)

        # Initialize recording variables
        self.running = False
        self.is_paused = False
        self.out = None
        self.filename = ""

    def start_recording(self):
        if self.running:
            QMessageBox.information(self, "Info", "Recording is already in progress.")
            return

        # Get options and start recording
        fps = int(self.fps_combobox.currentText())
        format = self.format_combobox.currentText()
        self.filename = os.path.join(self.recording_folder, f'screen_recording_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.{format}')
        fourcc = cv2.VideoWriter_fourcc(*"mp4v" if format == "mp4" else "XVID")
        self.out = cv2.VideoWriter(self.filename, fourcc, fps, pyautogui.size())

        if self.countdown_checkbox.isChecked():
            for i in range(3, 0, -1):
                print(f"Recording starts in {i}...")
                time.sleep(1)

        self.running = True
        self.start_button.hide()
        self.pause_button.show()
        self.stop_button.show()
        self.rec_icon.show()

        if self.audio_checkbox.isChecked():
            self.audio_filename = tempfile.mktemp(suffix=".wav")
            self.audio_frames = []  # Store audio frames here
            self.audio_thread = threading.Thread(target=self.record_audio)
            self.audio_thread.start()

        threading.Thread(target=self.record, daemon=True).start()

    def toggle_pause(self):
        if self.running:
            self.is_paused = not self.is_paused
            self.pause_button.setText("Resume" if self.is_paused else "Pause")

    def record(self):
        while self.running:
            if not self.is_paused:
                frame = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
                if self.timestamp_checkbox.isChecked():
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                self.out.write(frame)
            time.sleep(1 / 30)

        self.out.release()

    def stop_recording(self):
        if not self.running:
            QMessageBox.information(self, "Info", "No recording is in progress.")
            return

        self.running = False
        self.pause_button.hide()
        self.stop_button.hide()
        self.rec_icon.hide()
        self.start_button.show()

        if self.audio_checkbox.isChecked() and hasattr(self, 'audio_thread'):
            self.audio_thread.join()

        if self.audio_checkbox.isChecked():
            self.combine_audio_video()

        QMessageBox.information(self, "Info", f"Recording saved as {self.filename}.")

    def record_audio(self):
        fs = 44100
        duration = 0.1
        channels = 2

        with sd.InputStream(samplerate=fs, channels=channels, dtype='int16') as stream:
            while self.running:
                if not self.is_paused:
                    audio_data = stream.read(int(duration * fs))[0]
                    self.audio_frames.append(audio_data)
                else:
                    time.sleep(0.1)

        with wave.open(self.audio_filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(b''.join(self.audio_frames))

    def combine_audio_video(self):
        video = VideoFileClip(self.filename)
        audio = AudioFileClip(self.audio_filename)
        video_with_audio = video.set_audio(audio)
        video_with_audio.write_videofile(self.filename, codec="libx264", audio_codec="aac")
        os.remove(self.audio_filename)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())