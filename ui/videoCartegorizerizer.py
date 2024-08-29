import sys
import os
from moviepy.editor import VideoFileClip
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPushButton, QVBoxLayout, QWidget, QLabel, QListWidget, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class VideoProcessingThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, videos, output_folder):
        super().__init__()
        self.videos = videos
        self.output_folder = output_folder

    def run(self):
        total_videos = len(self.videos)
        for i, video_path in enumerate(self.videos):
            self.categorize_and_move(video_path)
            progress_percentage = int(((i + 1) / total_videos) * 100)
            self.progress.emit(progress_percentage)
        self.finished.emit()

    def categorize_and_move(self, video_path):
        try:
            # Extract the first frame of the video
            clip = VideoFileClip(video_path)
            frame = clip.get_frame(0)  # Extract the frame at the start of the video

            # For simplicity, use the video filename as the category
            # You might replace this with a real categorization algorithm
            category = os.path.splitext(os.path.basename(video_path))[0]

            # Create category folder if it does not exist
            category_folder = os.path.join(self.output_folder, category)
            if not os.path.exists(category_folder):
                os.makedirs(category_folder)

            # Move video to category folder
            video_name = os.path.basename(video_path)
            output_path = os.path.join(category_folder, video_name)
            os.rename(video_path, output_path)

        except Exception as e:
            print(f"Error processing video {video_path}: {str(e)}")

class VideoCategorizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Video Categorizer')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.label = QLabel('Select videos and output folder')
        layout.addWidget(self.label)

        self.selectVideosBtn = QPushButton('Select Videos')
        self.selectVideosBtn.clicked.connect(self.select_videos)
        layout.addWidget(self.selectVideosBtn)

        self.videoList = QListWidget()
        layout.addWidget(self.videoList)

        self.selectFolderBtn = QPushButton('Select Output Folder')
        self.selectFolderBtn.clicked.connect(self.select_folder)
        layout.addWidget(self.selectFolderBtn)

        self.processVideosBtn = QPushButton('Process Videos')
        self.processVideosBtn.clicked.connect(self.process_videos)
        layout.addWidget(self.processVideosBtn)

        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 100)
        layout.addWidget(self.progressBar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.videos = []
        self.output_folder = ''
        self.thread = None

    def select_videos(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Videos", "", "Video Files (*.mp4 *.avi *.mov)",
                                                options=options)
        if files:
            self.videos = files
            self.videoList.clear()
            self.videoList.addItems([os.path.basename(video) for video in self.videos])

    def select_folder(self):
        options = QFileDialog.Options()
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", options=options)
        if folder:
            self.output_folder = folder

    def process_videos(self):
        if not self.videos or not self.output_folder:
            self.label.setText("Please select videos and output folder.")
            return

        if self.thread and self.thread.isRunning():
            self.thread.terminate()

        self.thread = VideoProcessingThread(self.videos, self.output_folder)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.processing_finished)
        self.thread.start()

    def update_progress(self, value):
        self.progressBar.setValue(value)

    def processing_finished(self):
        self.label.setText("Processing complete!")
        self.progressBar.setValue(100)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoCategorizerApp()
    ex.show()
    sys.exit(app.exec_())
