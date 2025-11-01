"""
爱心弹窗组件
透明、无边框、美观的弹窗实现
"""
import random
import numpy as np
from pathlib import Path
from typing import List
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtProperty
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QPainterPath, QFont
from loguru import logger

from config import config, BUILTIN_COLOR_THEMES
from heart_trajectory import HeartTrajectory


class HeartWindow(QWidget):
    """爱心弹窗类"""
    
    def __init__(self, message: str, color_theme: dict, trajectory: HeartTrajectory,
                 start_progress: float, start_delay: int = 0):
        """
        初始化弹窗
        
        Args:
            message: 要显示的关心语句
            color_theme: 颜色主题字典
            trajectory: 爱心轨迹对象
            start_progress: 起始进度位置 (0.0-1.0)
            start_delay: 启动延迟（毫秒）
        """
        super().__init__()
        
        self.message = message
        self.color_theme = color_theme
        self.trajectory = trajectory
        self.progress = start_progress
        self._opacity = 0.0
        self._current_scale = 1.0
        self.start_delay = start_delay
        
        logger.debug(f"创建弹窗: message='{message[:10]}...', start_progress={start_progress:.2f}")
        
        # 初始化UI
        self._init_ui()
        
        # 初始化动画定时器
        self._init_animation()
        
    def _init_ui(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |  # 置顶
            Qt.FramelessWindowHint |    # 无边框
            Qt.Tool                      # 工具窗口（不显示在任务栏）
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        # 固定窗口大小（稍微大一点，方便阅读）
        self.setFixedSize(320, 120)
        
        # 创建布局
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        
        # 创建文本标签
        self.label = QLabel(self.message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        
        # 设置字体
        font = QFont("Microsoft YaHei", 14, QFont.Bold)
        self.label.setFont(font)
        self.label.setStyleSheet(f"color: {self.color_theme['text']}; background: transparent;")
        
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # 初始位置（在轨迹起点）
        x, y = self.trajectory.get_point_at_progress(self.progress)
        self.move(int(x - 160), int(y - 60))
        
    def _init_animation(self):
        """初始化动画"""
        # 运动动画定时器
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._update_position)
        
        # 淡入动画定时器
        self.fade_in_timer = QTimer(self)
        self.fade_in_timer.timeout.connect(self._fade_in)
        
        # 延迟启动
        if self.start_delay > 0:
            QTimer.singleShot(self.start_delay, self._start_animation)
        else:
            self._start_animation()
    
    def _start_animation(self):
        """启动动画"""
        self.show()
        self.fade_in_timer.start(20)
        
    def _fade_in(self):
        """淡入效果"""
        self._opacity += 0.05
        if self._opacity >= 0.95:
            self._opacity = 0.95
            self.fade_in_timer.stop()
            # 淡入完成后开始运动
            self.animation_timer.start(16)  # 约60fps
        self.update()
    
    def _update_position(self):
        """更新窗口位置和动画效果"""
        # 更新进度（速度稍慢，方便看清内容）
        self.progress += 1.0 / 1500  # 25秒完成一圈
        
        if self.progress >= 1.0:
            self.progress = self.progress % 1.0
        
        # 获取新位置
        x, y = self.trajectory.get_point_at_progress(self.progress)
        
        # 轻微的脉动缩放效果
        scale_factor = 0.98 + 0.04 * abs(np.sin(self.progress * 2 * np.pi))
        self._current_scale = scale_factor
        
        # 移动窗口
        self.move(int(x - 160), int(y - 60))
    
    def paintEvent(self, event):
        """绘制窗口背景（圆角矩形 + 渐变）"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setOpacity(self._opacity)
        
        # 应用缩放
        if self._current_scale != 1.0:
            painter.save()
            center_x = self.width() / 2
            center_y = self.height() / 2
            painter.translate(center_x, center_y)
            painter.scale(self._current_scale, self._current_scale)
            painter.translate(-center_x, -center_y)
        
        # 创建圆角矩形路径
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        
        # 创建线性渐变
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(self.color_theme['bg_start']))
        gradient.setColorAt(1, QColor(self.color_theme['bg_end']))
        
        # 填充背景
        painter.fillPath(path, gradient)
        
        # 绘制边框
        painter.setPen(QColor(self.color_theme['shadow']))
        painter.drawPath(path)
        
        if self._current_scale != 1.0:
            painter.restore()
        
        painter.end()
    
    def fade_out_and_close(self):
        """淡出并关闭窗口"""
        if hasattr(self, 'animation_timer'):
            self.animation_timer.stop()
        self.fade_out_timer = QTimer(self)
        self.fade_out_timer.timeout.connect(self._fade_out)
        self.fade_out_timer.start(20)
    
    def _fade_out(self):
        """淡出效果"""
        self._opacity -= 0.05
        if self._opacity <= 0:
            self._opacity = 0
            self.fade_out_timer.stop()
            self.close()
        self.update()
    
    def mousePressEvent(self, event):
        """鼠标点击事件 - 点击关闭"""
        if event.button() == Qt.LeftButton:
            logger.info(f"用户点击关闭弹窗")
            self.fade_out_and_close()
    
    @pyqtProperty(float)
    def opacity(self):
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.update()


class HeartWindowManager:
    """弹窗管理器 - 管理多个弹窗"""
    
    def __init__(self):
        self.windows: List[HeartWindow] = []
        self.messages: List[str] = []
        logger.info("弹窗管理器初始化")
        
    def load_messages(self, file_path: Path):
        """从文件加载关心语句"""
        try:
            if not file_path.exists():
                logger.error(f"消息文件不存在: {file_path}")
                self._use_default_messages()
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                self.messages = [line.strip() for line in f if line.strip()]
            
            logger.success(f"成功加载 {len(self.messages)} 条关心语句")
            
        except Exception as e:
            logger.error(f"加载语句文件失败: {e}")
            self._use_default_messages()
    
    def _use_default_messages(self):
        """使用默认语句"""
        self.messages = [
            "记得按时吃饭哦 💖", "今天也要开心呀 ✨", "累了就休息一下吧 🌟",
            "你真的很棒 💕", "别忘了多喝水 💧", "要好好照顾自己 ❤️"
        ]
        logger.warning(f"使用默认语句，共 {len(self.messages)} 条")
    
    def create_windows(self, screen_width: int, screen_height: int, num_popups: int):
        """
        创建均匀分布在轨迹上的弹窗
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            num_popups: 弹窗数量
        """
        logger.info(f"开始创建 {num_popups} 个弹窗，均匀分布在爱心轨迹上")
        
        # 创建更大的轨迹（屏幕中心，增大scale）
        # 根据屏幕大小动态调整
        scale = min(screen_width, screen_height) * 0.25  # 使用屏幕尺寸的25%
        trajectory = HeartTrajectory(scale=scale)
        center_x = screen_width / 2
        center_y = screen_height / 2
        trajectory.set_center(center_x, center_y)
        trajectory.generate_points()
        
        logger.info(f"爱心轨迹: scale={scale:.0f}, center=({center_x:.0f}, {center_y:.0f})")
        
        # 计算每个弹窗的起始位置（均匀分布，避免重叠）
        for i in range(num_popups):
            # 均匀分布的进度值
            start_progress = i / num_popups
            
            # 循环选择消息
            message = self.messages[i % len(self.messages)]
            
            # 循环选择颜色主题
            color_theme = BUILTIN_COLOR_THEMES[i % len(BUILTIN_COLOR_THEMES)]
            
            # 启动延迟（让弹窗依次出现，更舒缓）
            start_delay = i * 150  # 每个延迟150ms
            
            # 创建窗口
            window = HeartWindow(
                message, 
                color_theme, 
                trajectory, 
                start_progress,
                start_delay
            )
            self.windows.append(window)
            
            logger.debug(f"创建弹窗 #{i+1}/{num_popups}: progress={start_progress:.3f}, theme={color_theme['name']}")
        
        logger.success(f"所有弹窗创建完成！")
    
    def close_all(self):
        """关闭所有弹窗"""
        logger.info(f"关闭所有弹窗，共 {len(self.windows)} 个")
        for window in self.windows:
            if window:
                window.fade_out_and_close()
        self.windows.clear()
