"""
配置管理模块 - 使用 Pydantic 和 JSON
"""
import json
from pathlib import Path
from pydantic import BaseModel, Field
from loguru import logger


# 项目根目录
BASE_DIR = Path(__file__).parent.parent.resolve()
CONFIG_FILE = BASE_DIR / "config.json"
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# 确保必要的目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


# 内置颜色主题（用户不需要配置）
BUILTIN_COLOR_THEMES = [
    {"name": "浪漫粉红", "bg_start": "#FF6B9D", "bg_end": "#FEC7D7", "text": "#FFFFFF", "shadow": "#FF1493"},
    {"name": "清新薄荷", "bg_start": "#A8E6CF", "bg_end": "#DCEDC8", "text": "#2E7D32", "shadow": "#4CAF50"},
    {"name": "温暖橙橘", "bg_start": "#FFD3B6", "bg_end": "#FFAAA5", "text": "#FFFFFF", "shadow": "#FF6F61"},
    {"name": "天空蓝", "bg_start": "#B5D8FF", "bg_end": "#E3F2FD", "text": "#1565C0", "shadow": "#2196F3"},
    {"name": "优雅紫", "bg_start": "#E1BEE7", "bg_end": "#F3E5F5", "text": "#6A1B9A", "shadow": "#9C27B0"},
    {"name": "活力黄", "bg_start": "#FFF9C4", "bg_end": "#FFEB3B", "text": "#F57F17", "shadow": "#FBC02D"},
    {"name": "宁静青", "bg_start": "#B2EBF2", "bg_end": "#E0F7FA", "text": "#006064", "shadow": "#00ACC1"},
    {"name": "甜蜜桃", "bg_start": "#FFCCBC", "bg_end": "#FFAB91", "text": "#FFFFFF", "shadow": "#FF5722"},
    {"name": "梦幻紫粉", "bg_start": "#F8BBD0", "bg_end": "#F48FB1", "text": "#FFFFFF", "shadow": "#E91E63"},
    {"name": "森林绿", "bg_start": "#C5E1A5", "bg_end": "#AED581", "text": "#33691E", "shadow": "#7CB342"},
]


class AppConfig(BaseModel):
    """应用配置"""
    num_popups: int = Field(default=24, ge=5, le=50, description="弹窗数量")
    messages_file: str = Field(default="messages.txt", description="消息文件名")
    
    @property
    def messages_path(self) -> Path:
        """获取消息文件完整路径"""
        return DATA_DIR / self.messages_file
    
    @classmethod
    def load_from_json(cls, config_path: Path = CONFIG_FILE) -> 'AppConfig':
        """从JSON文件加载配置"""
        try:
            if not config_path.exists():
                logger.warning(f"配置文件不存在: {config_path}, 使用默认配置")
                config = cls()
                config.save_to_json(config_path)
                return config
            
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"成功加载配置文件: {config_path}")
            return cls(**data)
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}, 使用默认配置")
            return cls()
    
    def save_to_json(self, config_path: Path = CONFIG_FILE):
        """保存配置到JSON文件"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(
                    self.model_dump(),
                    f,
                    ensure_ascii=False,
                    indent=2
                )
            logger.info(f"配置已保存到: {config_path}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")


# 全局配置实例
config = AppConfig.load_from_json()


def setup_logger():
    """配置日志系统"""
    logger.remove()
    
    # 控制台输出
    logger.add(
        sink=lambda msg: print(msg, end=''),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # 文件输出
    log_file = LOG_DIR / "heartcare_{time:YYYY-MM-DD}.log"
    logger.add(
        sink=str(log_file),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        rotation="10 MB",
        retention="7 days",
        encoding='utf-8',
        enqueue=True
    )
    
    logger.info("=" * 60)
    logger.info("爱心关怀弹窗程序启动")
    logger.info(f"弹窗数量: {config.num_popups} (建议: 15-30)")
    logger.info("按 ESC 键退出程序")
    logger.info("=" * 60)


# 初始化日志
setup_logger()


if __name__ == '__main__':
    print(f"\n当前配置:")
    print(f"弹窗数量: {config.num_popups} (建议: 15-30)")
    print(f"消息文件: {config.messages_path}")
    print(f"内置主题数: {len(BUILTIN_COLOR_THEMES)}")
