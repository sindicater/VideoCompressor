import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QLabel, QMessageBox
)

class VideoRenamerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Video Renamer')

        # Layout
        layout = QVBoxLayout()

        # Instructions Label
        self.label = QLabel('Select videos to rename and enter the desired format (e.g., v for v1, v2, ...)', self)
        layout.addWidget(self.label)

        # Input Field for Filename Format
        self.format_input = QLineEdit(self)
        self.format_input.setPlaceholderText('Enter filename format (e.g., v)')
        layout.addWidget(self.format_input)

        # Button to select videos
        self.select_btn = QPushButton('Select Videos', self)
        self.select_btn.clicked.connect(self.select_videos)
        layout.addWidget(self.select_btn)

        # Button to rename videos
        self.rename_btn = QPushButton('Rename Videos', self)
        self.rename_btn.clicked.connect(self.rename_videos)
        layout.addWidget(self.rename_btn)

        self.setLayout(layout)

    def select_videos(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.files, _ = QFileDialog.getOpenFileNames(self, "Select Videos to Rename", "",
                                                     "Video Files (*.mp4 *.avi *.mkv *.mov *.flv)", options=options)
        if self.files:
            QMessageBox.information(self, "Selected Files", f"{len(self.files)} files selected.")

    def rename_videos(self):
        if not hasattr(self, 'files') or not self.files:
            QMessageBox.warning(self, "No Files", "No video files selected. Please select files first.")
            return

        filename_format = self.format_input.text().strip()
        if not filename_format:
            QMessageBox.warning(self, "Invalid Format", "Please enter a valid filename format.")
            return

        # Renaming files
        for i, file_path in enumerate(self.files, start=1):
            directory = os.path.dirname(file_path)
            extension = os.path.splitext(file_path)[1]
            new_filename = f"{filename_format}{i}{extension}"
            new_file_path = os.path.join(directory, new_filename)

            try:
                os.rename(file_path, new_file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while renaming {file_path}: {e}")
                return

        QMessageBox.information(self, "Success", "Files renamed successfully!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoRenamerApp()
    ex.show()
    sys.exit(app.exec_())
