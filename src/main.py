"""
爱心弹窗主程序
显示沿爱心轨迹运动的关心语句弹窗
按 ESC 键退出
"""
import sys
import threading
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon
from loguru import logger

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    logger.warning("keyboard 库未安装，ESC键监听将不可用")
    logger.warning("请运行: pip install keyboard")

from config import config
from heart_window import HeartWindowManager


class KeyboardListener(QObject):
    """全局键盘监听器 - 独立线程监听ESC键"""
    
    # 定义信号，用于线程间通信
    esc_pressed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.listening = False
        self.listener_thread = None
        
    def start_listening(self):
        """启动监听线程"""
        if not KEYBOARD_AVAILABLE:
            logger.error("keyboard 库未安装，无法启动ESC监听")
            return
        
        if self.listening:
            logger.warning("ESC监听已经在运行")
            return
        
        self.listening = True
        
        # 在独立线程中启动监听
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()
        
        logger.success("✅ 全局ESC键监听已启动（独立线程）")
    
    def _listen_loop(self):
        """监听循环 - 在独立线程中运行"""
        try:
            # 注册ESC键的回调
            keyboard.on_press_key('esc', self._on_esc_press, suppress=False)
            
            # 保持线程运行
            while self.listening:
                threading.Event().wait(0.1)
                
        except Exception as e:
            logger.error(f"键盘监听线程异常: {e}")
    
    def _on_esc_press(self, event):
        """ESC键按下的回调函数 - 在监听线程中执行"""
        logger.info("🔔 检测到 ESC 键（全局监听）")
        # 发送信号到主线程
        self.esc_pressed.emit()
    
    def stop_listening(self):
        """停止监听"""
        if not self.listening:
            return
        
        self.listening = False
        
        try:
            if KEYBOARD_AVAILABLE:
                keyboard.unhook_all()
        except:
            pass
        
        logger.info("ESC键监听已停止")


class HeartCareApp:
    """爱心关怀应用主类"""
    
    def __init__(self):
        """初始化应用"""
        logger.info("初始化爱心关怀应用...")
        
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("爱心关怀弹窗")
        self.app.setQuitOnLastWindowClosed(False)
        
        # 创建键盘监听器
        self.keyboard_listener = KeyboardListener()
        # 连接信号到退出槽函数
        self.keyboard_listener.esc_pressed.connect(self.quit_app)
        # 启动监听
        self.keyboard_listener.start_listening()
        
        # 获取屏幕尺寸
        screen = self.app.primaryScreen().geometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        logger.info(f"屏幕分辨率: {self.screen_width}x{self.screen_height}")
        
        # 初始化弹窗管理器
        self.manager = HeartWindowManager()
        self.manager.load_messages(config.messages_path)
        
        # 创建系统托盘图标
        self._create_tray_icon()
        
        # 启动弹窗
        self._start_popups()
    
    def _create_tray_icon(self):
        """创建系统托盘图标和菜单"""
        logger.info("创建系统托盘图标...")
        
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 重新显示
        show_action = QAction("💖 重新显示", self.app)
        show_action.triggered.connect(self._restart_popups)
        tray_menu.addAction(show_action)
        
        # 隐藏弹窗
        hide_action = QAction("🙈 隐藏弹窗", self.app)
        hide_action.triggered.connect(self._hide_popups)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        # 退出
        quit_action = QAction("❌ 退出 (ESC)", self.app)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip("爱心关怀弹窗 💖\n按 ESC 键退出")
        self.tray_icon.show()
        
        # 托盘图标双击事件
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        logger.success("系统托盘图标创建成功")
    
    def _on_tray_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            logger.info("用户双击托盘图标")
            self._restart_popups()
    
    def _start_popups(self):
        """启动弹窗显示"""
        logger.info(f"开始显示 {config.num_popups} 个弹窗...")
        
        # 创建均匀分布在轨迹上的弹窗
        self.manager.create_windows(
            self.screen_width,
            self.screen_height,
            config.num_popups
        )
        
        logger.success("弹窗已全部启动！")
        self.tray_icon.showMessage(
            "爱心关怀 💖",
            f"已启动 {config.num_popups} 个弹窗\n\n⌨️ 按 ESC 键退出程序\n🖱️ 点击弹窗关闭单个",
            QSystemTrayIcon.Information,
            3000
        )
    
    def _restart_popups(self):
        """重新显示弹窗"""
        logger.info("用户请求重新显示弹窗")
        self.manager.close_all()
        QTimer.singleShot(500, self._start_popups)
    
    def _hide_popups(self):
        """隐藏所有弹窗"""
        logger.info("用户请求隐藏弹窗")
        self.manager.close_all()
        self.tray_icon.showMessage(
            "爱心关怀 💖",
            "已隐藏所有弹窗",
            QSystemTrayIcon.Information,
            1000
        )
    
    def quit_app(self):
        """退出应用 - 由ESC监听线程触发"""
        logger.info("=" * 60)
        logger.info("⌨️ 接收到退出信号（ESC键）")
        
        # 停止键盘监听
        self.keyboard_listener.stop_listening()
        
        # 关闭所有弹窗
        self.manager.close_all()
        
        # 隐藏托盘图标
        self.tray_icon.hide()
        
        # 延迟退出，确保资源清理完成
        QTimer.singleShot(300, self._do_quit)
    
    def _do_quit(self):
        """执行退出"""
        logger.info("应用已退出")
        logger.info("=" * 60)
        self.app.quit()
    
    def run(self):
        """运行应用"""
        logger.info("=" * 60)
        logger.info("💖 爱心关怀弹窗程序运行中")
        logger.info("=" * 60)
        logger.info("操作说明：")
        logger.info("  ⌨️  按 ESC 键：退出程序（全局监听）")
        logger.info("  🖱️  点击弹窗：关闭该弹窗")
        logger.info("  🖱️  双击托盘：重新显示")
        logger.info("=" * 60)
        if config.num_popups > 30:
            logger.warning(f"⚠️  当前弹窗数量为 {config.num_popups}，可能较密集，建议设置为 15-30 个")
        logger.info("=" * 60)
        
        return self.app.exec_()


def main():
    """主函数"""
    try:
        if not config.messages_path.exists():
            logger.warning(f"未找到消息文件: {config.messages_path}")
            logger.warning("将使用默认消息")
        
        # 创建并运行应用
        app = HeartCareApp()
        exit_code = app.run()
        
        logger.info(f"程序退出，退出码: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.exception(f"程序发生异常: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
