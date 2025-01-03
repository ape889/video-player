import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QUrl, QTimer, QSize
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置窗口无边框
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # 获取视频文件夹中的所有视频
        folder_path = "/Users/ape/Desktop/视频播放器"  # 替换为您的视频文件夹路径
        self.video_files = []
        for file in os.listdir(folder_path):
            if file.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
                self.video_files.append(os.path.join(folder_path, file))
        
        if not self.video_files:
            print("文件夹中没有找到视频文件！")
            sys.exit()
            
        self.current_video_index = 0
        
        # 创建主窗口部件
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        widget.setLayout(layout)

        # 创建视频显示区域
        self.video_widget = QVideoWidget()
        self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)  # 保持视频比例
        layout.addWidget(self.video_widget)

        # 设置窗口大小为竖屏尺寸（根据需要调整）
        self.resize(540, 960)  # 适合竖屏视频的尺寸

        # 将窗口移动到屏幕中央
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2,
                  (screen.height() - self.height()) // 2)

        # 创建音频输出和媒体播放器
        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setAudioOutput(self.audio_output)

        # 预加载下一个视频
        self.next_player = QMediaPlayer()
        self.next_audio_output = QAudioOutput()
        self.next_player.setAudioOutput(self.next_audio_output)
        
        # 创建定时器来检查视频状态
        self.timer = QTimer(self)
        self.timer.setInterval(100)  # 每100毫秒检查一次
        self.timer.timeout.connect(self.check_video_status)
        self.timer.start()

        # 开始播放第一个视频并预加载下一个
        self.play_current_video()
        self.preload_next_video()

    def play_current_video(self):
        video_path = self.video_files[self.current_video_index]
        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        self.media_player.play()

    def preload_next_video(self):
        next_index = (self.current_video_index + 1) % len(self.video_files)
        next_video = self.video_files[next_index]
        self.next_player.setSource(QUrl.fromLocalFile(next_video))

    def switch_to_next_video(self):
        # 切换播放器
        temp_player = self.media_player
        temp_audio = self.audio_output
        
        self.media_player = self.next_player
        self.audio_output = self.next_audio_output
        self.media_player.setVideoOutput(self.video_widget)
        
        self.next_player = temp_player
        self.next_audio_output = temp_audio
        
        # 更新索引并预加载下一个视频
        self.current_video_index = (self.current_video_index + 1) % len(self.video_files)
        self.media_player.play()
        self.preload_next_video()

    def check_video_status(self):
        # 检查视频是否接近结束
        if (self.media_player.duration() - self.media_player.position() < 200 and 
            self.media_player.duration() > 0):
            self.switch_to_next_video()

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

def main():
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 