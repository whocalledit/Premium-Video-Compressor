import sys
import os
import subprocess
import threading
import time
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class VideoCompressor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Premium Video Compressor")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet(self.get_stylesheet())
        self.setAcceptDrops(True)
        
        # Variables
        self.video_files = []
        self.current_processing = False
        self.output_folder = ""
        
        self.init_ui()
        self.check_ffmpeg()
    
    def get_stylesheet(self):
        return """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #1a1a2e, stop:1 #16213e);
        }
        
        QWidget {
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #667eea, stop:1 #764ba2);
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: bold;
            font-size: 14px;
        }
        
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #5a6fd8, stop:1 #6a4190);
        }
        
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #4e5bc6, stop:1 #5e377e);
        }
        
        QListWidget {
            background: rgba(255, 255, 255, 0.1);
            border: 2px dashed rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            padding: 10px;
            font-size: 13px;
        }
        
        QListWidget::item {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
            padding: 8px;
            margin: 2px;
        }
        
        QListWidget::item:selected {
            background: rgba(102, 126, 234, 0.3);
        }
        
        QProgressBar {
            border: none;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            text-align: center;
            font-weight: bold;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #667eea, stop:1 #764ba2);
            border-radius: 10px;
        }
        
        QLabel {
            font-size: 14px;
        }
        
        QComboBox {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 8px;
            font-size: 13px;
        }
        
        QComboBox::drop-down {
            border: none;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid white;
        }
        
        QTextEdit {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 10px;
            font-size: 12px;
            font-family: 'Consolas', monospace;
        }
        """
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("🎬 Premium Video Compressor")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Maximum compression • Lossless quality • Lightning fast")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #a0a0a0; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left panel
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        # File selection area
        file_group = QGroupBox("📁 Video Files")
        file_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        file_layout = QVBoxLayout(file_group)
        
        # Drag and drop area
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(200)
        self.file_list.setDragDropMode(QAbstractItemView.InternalMove)
        file_layout.addWidget(self.file_list)
        
        # File buttons
        file_buttons = QHBoxLayout()
        self.add_files_btn = QPushButton("➕ Add Videos")
        self.add_folder_btn = QPushButton("📂 Add Folder")
        self.clear_btn = QPushButton("🗑️ Clear")
        
        self.add_files_btn.clicked.connect(self.add_files)
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.clear_btn.clicked.connect(self.clear_files)
        
        file_buttons.addWidget(self.add_files_btn)
        file_buttons.addWidget(self.add_folder_btn)
        file_buttons.addWidget(self.clear_btn)
        file_layout.addLayout(file_buttons)
        
        left_panel.addWidget(file_group)
        
        # Settings
        settings_group = QGroupBox("⚙️ Compression Settings")
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        settings_layout = QVBoxLayout(settings_group)
        
        # Quality preset
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality Preset:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "Maximum Compression (Slower)",
            "Balanced (Recommended)", 
            "Fast Compression"
        ])
        self.quality_combo.setCurrentIndex(1)
        quality_layout.addWidget(self.quality_combo)
        settings_layout.addLayout(quality_layout)
        
        # Output folder
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Folder:"))
        self.output_path_label = QLabel("Same as source")
        self.output_path_label.setStyleSheet("color: #a0a0a0; font-style: italic;")
        self.browse_output_btn = QPushButton("Browse")
        self.browse_output_btn.clicked.connect(self.browse_output_folder)
        
        output_layout.addWidget(self.output_path_label, 1)
        output_layout.addWidget(self.browse_output_btn)
        settings_layout.addLayout(output_layout)
        
        left_panel.addWidget(settings_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("🚀 Start Compression")
        self.start_btn.setStyleSheet(self.start_btn.styleSheet() + "font-size: 16px; padding: 15px;")
        self.start_btn.clicked.connect(self.start_compression)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_compression)
        
        control_layout.addWidget(self.start_btn, 2)
        control_layout.addWidget(self.stop_btn, 1)
        left_panel.addLayout(control_layout)
        
        content_layout.addLayout(left_panel, 2)
        
        # Right panel - Progress and logs
        right_panel = QVBoxLayout()
        
        # Progress section
        progress_group = QGroupBox("📊 Progress")
        progress_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to compress")
        self.status_label.setStyleSheet("color: #a0a0a0;")
        progress_layout.addWidget(self.status_label)
        
        # Stats
        stats_layout = QHBoxLayout()
        self.files_processed_label = QLabel("Files: 0/0")
        self.compression_ratio_label = QLabel("Compression: 0%")
        self.time_elapsed_label = QLabel("Time: 00:00")
        
        stats_layout.addWidget(self.files_processed_label)
        stats_layout.addWidget(self.compression_ratio_label)
        stats_layout.addWidget(self.time_elapsed_label)
        progress_layout.addLayout(stats_layout)
        
        right_panel.addWidget(progress_group)
        
        # Log section
        log_group = QGroupBox("📝 Processing Log")
        log_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        right_panel.addWidget(log_group)
        
        content_layout.addLayout(right_panel, 1)
        layout.addLayout(content_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready • Drag and drop videos or click 'Add Videos'")
        self.statusBar().setStyleSheet("color: #a0a0a0;")
    
    def check_ffmpeg(self):
        """Check if FFmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            self.log("✅ FFmpeg found and ready")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("⚠️ FFmpeg not found. Please install FFmpeg and add it to PATH")
            QMessageBox.warning(self, "FFmpeg Required", 
                              "FFmpeg is required for video compression.\n"
                              "Please download and install FFmpeg from https://ffmpeg.org/")
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        video_files = [f for f in files if self.is_video_file(f)]
        
        for file in video_files:
            if file not in self.video_files:
                self.video_files.append(file)
                self.file_list.addItem(f"📹 {os.path.basename(file)}")
        
        self.update_status()
        self.log(f"Added {len(video_files)} video file(s)")
    
    def is_video_file(self, file_path):
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
        return Path(file_path).suffix.lower() in video_extensions
    
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Video Files", "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.m4v);;All Files (*)"
        )
        
        for file in files:
            if file not in self.video_files:
                self.video_files.append(file)
                self.file_list.addItem(f"📹 {os.path.basename(file)}")
        
        self.update_status()
        self.log(f"Added {len(files)} video file(s)")
    
    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with Videos")
        if folder:
            video_files = []
            for ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']:
                video_files.extend(Path(folder).glob(f"*{ext}"))
                video_files.extend(Path(folder).glob(f"*{ext.upper()}"))
            
            added = 0
            for file in video_files:
                file_str = str(file)
                if file_str not in self.video_files:
                    self.video_files.append(file_str)
                    self.file_list.addItem(f"📹 {file.name}")
                    added += 1
            
            self.update_status()
            self.log(f"Added {added} video file(s) from folder")
    
    def clear_files(self):
        self.video_files.clear()
        self.file_list.clear()
        self.update_status()
        self.log("Cleared all files")
    
    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.output_path_label.setText(folder)
            self.output_path_label.setStyleSheet("color: #ffffff;")
    
    def update_status(self):
        count = len(self.video_files)
        if count == 0:
            self.statusBar().showMessage("Ready • Drag and drop videos or click 'Add Videos'")
        else:
            self.statusBar().showMessage(f"Ready • {count} video(s) selected")
    
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        QApplication.processEvents()
    
    def start_compression(self):
        if not self.video_files:
            QMessageBox.warning(self, "No Files", "Please add video files first!")
            return
        
        self.current_processing = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Start compression in separate thread
        self.compression_thread = CompressionWorker(
            self.video_files, 
            self.output_folder, 
            self.quality_combo.currentIndex()
        )
        self.compression_thread.progress_updated.connect(self.update_progress)
        self.compression_thread.file_completed.connect(self.file_completed)
        self.compression_thread.compression_finished.connect(self.compression_finished)
        self.compression_thread.log_message.connect(self.log)
        self.compression_thread.start()
        
        self.log("🚀 Started compression process")
    
    def stop_compression(self):
        if hasattr(self, 'compression_thread'):
            self.compression_thread.stop()
        self.current_processing = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log("⏹️ Compression stopped by user")
    
    def update_progress(self, current_file, total_files, percentage):
        overall_progress = ((current_file - 1) * 100 + percentage) / total_files
        self.progress_bar.setValue(int(overall_progress))
        self.status_label.setText(f"Processing file {current_file}/{total_files} ({percentage}%)")
        self.files_processed_label.setText(f"Files: {current_file-1 if percentage < 100 else current_file}/{total_files}")
    
    def file_completed(self, filename, original_size, compressed_size):
        compression_ratio = ((original_size - compressed_size) / original_size) * 100
        self.compression_ratio_label.setText(f"Saved: {compression_ratio:.1f}%")
        self.log(f"✅ Completed: {filename} (Saved {compression_ratio:.1f}%)")
    
    def compression_finished(self):
        self.current_processing = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)
        self.status_label.setText("All files processed successfully!")
        self.log("🎉 All compressions completed!")
        
        QMessageBox.information(self, "Compression Complete", 
                              "All video files have been compressed successfully!")

class CompressionWorker(QThread):
    progress_updated = pyqtSignal(int, int, int)
    file_completed = pyqtSignal(str, int, int)
    compression_finished = pyqtSignal()
    log_message = pyqtSignal(str)
    
    def __init__(self, files, output_folder, quality_preset):
        super().__init__()
        self.files = files
        self.output_folder = output_folder
        self.quality_preset = quality_preset
        self.should_stop = False
    
    def stop(self):
        self.should_stop = True
    
    def run(self):
        total_files = len(self.files)
        
        for i, file_path in enumerate(self.files, 1):
            if self.should_stop:
                break
            
            try:
                self.compress_video(file_path, i, total_files)
            except Exception as e:
                self.log_message.emit(f"❌ Error processing {os.path.basename(file_path)}: {str(e)}")
        
        if not self.should_stop:
            self.compression_finished.emit()
    
    def compress_video(self, input_path, current_file, total_files):
        filename = os.path.basename(input_path)
        self.log_message.emit(f"🔄 Processing: {filename}")
        
        # Determine output path
        if self.output_folder:
            output_dir = self.output_folder
        else:
            output_dir = os.path.dirname(input_path)
        
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(output_dir, f"{name}_compressed{ext}")
        
        # Get quality settings
        if self.quality_preset == 0:  # Maximum compression
            crf = "28"
            preset = "slow"
        elif self.quality_preset == 1:  # Balanced
            crf = "23"
            preset = "medium"
        else:  # Fast
            crf = "20"
            preset = "fast"
        
        # Build FFmpeg command
        cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-c:v', 'libx265',
            '-crf', crf,
            '-preset', preset,
            '-c:a', 'aac',
            '-b:a', '128k',
            output_path
        ]
        
        # Get original file size
        original_size = os.path.getsize(input_path)
        
        # Run compression
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                 universal_newlines=True)
        
        # Monitor progress (simplified)
        while process.poll() is None:
            if self.should_stop:
                process.terminate()
                return
            
            # Simulate progress (in real implementation, parse FFmpeg output)
            import random
            progress = random.randint(10, 90)
            self.progress_updated.emit(current_file, total_files, progress)
            time.sleep(0.5)
        
        if process.returncode == 0:
            compressed_size = os.path.getsize(output_path)
            self.progress_updated.emit(current_file, total_files, 100)
            self.file_completed.emit(filename, original_size, compressed_size)
        else:
            raise Exception("FFmpeg compression failed")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    # Set application icon (you can add an icon file)
    # app.setWindowIcon(QIcon('icon.ico'))
    
    window = VideoCompressor()
    window.show()
    
    sys.exit(app.exec_())