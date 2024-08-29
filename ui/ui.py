import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QVBoxLayout, QLabel, QListWidget, \
    QProgressBar, QWidget, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from moviepy.editor import VideoFileClip

class VideoCompressorThread(QThread):
    update_progress = pyqtSignal(int)
    compression_finished = pyqtSignal(bool, str)

    def __init__(self, selected_files, output_folder):
        super().__init__()
        self.selected_files = selected_files
        self.output_folder = output_folder

    def run(self):
        try:
            total_files = len(self.selected_files)
            for index, file in enumerate(self.selected_files):
                output_file = os.path.join(self.output_folder, os.path.basename(file))

                # Compress video using MoviePy
                clip = VideoFileClip(file)
                clip_resized = clip.resize(height=480)  # Resize to 480p
                clip_resized.write_videofile(output_file, codec="libx264", preset="medium", bitrate="800k", threads=4)

                # Ensure clip is closed to free resources
                clip.close()

                # Update progress
                self.update_progress.emit(int(((index + 1) / total_files) * 100))

            self.compression_finished.emit(True, "All videos have been compressed successfully!")
        except Exception as e:
            self.compression_finished.emit(False, str(e))

class VideoCompressorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window settings
        self.setWindowTitle("Video Compressor")
        self.setGeometry(100, 100, 600, 400)

        # Layout
        self.layout = QVBoxLayout()

        # File selection button
        self.file_button = QPushButton("Select Videos")
        self.file_button.clicked.connect(self.select_files)
        self.layout.addWidget(self.file_button)

        # Selected files display
        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)

        # Video count label
        self.count_label = QLabel("Total Videos: 0")
        self.layout.addWidget(self.count_label)

        # Initial size label
        self.size_label = QLabel("Total Size: 0 MB")
        self.layout.addWidget(self.size_label)

        # Folder selection button
        self.folder_button = QPushButton("Select Output Folder")
        self.folder_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.folder_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)

        # Compress button
        self.compress_button = QPushButton("Start Compression")
        self.compress_button.clicked.connect(self.compress_videos)
        self.layout.addWidget(self.compress_button)

        # Set the central widget
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        # Variables
        self.selected_files = []
        self.output_folder = ""

    def select_files(self):
        try:
            options = QFileDialog.Options()
            files, _ = QFileDialog.getOpenFileNames(self, "Select Video Files", "", "Videos (*.mp4 *.avi *.mov *.mkv)",
                                                    options=options)
            if files:
                self.selected_files = files
                self.file_list.clear()
                self.file_list.addItems(files)
                self.update_video_count()
                self.calculate_initial_size()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while selecting files: {str(e)}")

    def update_video_count(self):
        total_videos = len(self.selected_files)
        self.count_label.setText(f"Total Videos: {total_videos}")

    def calculate_initial_size(self):
        try:
            total_size = sum(os.path.getsize(file) for file in self.selected_files) / (1024 * 1024)
            self.size_label.setText(f"Total Size: {total_size:.2f} MB")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while calculating size: {str(e)}")

    def select_folder(self):
        try:
            self.output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while selecting folder: {str(e)}")

    def compress_videos(self):
        if not self.selected_files or not self.output_folder:
            QMessageBox.warning(self, "Warning", "Please select both videos and an output folder before starting compression.")
            return

        try:
            # Disable the button to prevent re-clicking during compression
            self.compress_button.setEnabled(False)
            self.progress_bar.setValue(0)

            # Create and start the compression thread
            self.compressor_thread = VideoCompressorThread(self.selected_files, self.output_folder)
            self.compressor_thread.update_progress.connect(self.progress_bar.setValue)
            self.compressor_thread.compression_finished.connect(self.compression_complete)
            self.compressor_thread.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during compression: {str(e)}")

    def compression_complete(self, success, message):
        self.compress_button.setEnabled(True)
        if success:
            self.progress_bar.setValue(100)
            self.calculate_final_size()
            QMessageBox.information(self, "Compression Complete", message)
        else:
            QMessageBox.critical(self, "Compression Failed", message)

    def calculate_final_size(self):
        try:
            total_size = sum(os.path.getsize(os.path.join(self.output_folder, os.path.basename(file))) for file in self.selected_files) / (1024 * 1024)
            self.size_label.setText(f"Compressed Videos Size: {total_size:.2f} MB")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while calculating the final size: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoCompressorApp()
    window.show()
    sys.exit(app.exec_())
