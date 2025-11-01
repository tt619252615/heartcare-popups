"""
爱心轨迹计算模块
使用参数方程生成心形曲线
"""
import numpy as np
from typing import List, Tuple
from loguru import logger


class HeartTrajectory:
    """爱心轨迹生成器"""
    
    def __init__(self, scale: float = 80, center_x: float = None, center_y: float = None):
        """
        初始化爱心轨迹生成器
        
        Args:
            scale: 爱心大小缩放系数
            center_x: 中心X坐标（屏幕坐标）
            center_y: 中心Y坐标（屏幕坐标）
        """
        self.scale = scale
        self.center_x = center_x
        self.center_y = center_y
        self.points = []
        
        logger.debug(f"创建爱心轨迹: scale={scale}, center=({center_x}, {center_y})")
        
    def generate_points(self, num_points: int = 360) -> List[Tuple[float, float]]:
        """
        生成爱心曲线上的点
        使用参数方程：
        x(t) = 16*sin³(t)
        y(t) = 13*cos(t) - 5*cos(2t) - 2*cos(3t) - cos(4t)
        
        Args:
            num_points: 生成点的数量（越多越平滑）
            
        Returns:
            List[Tuple[float, float]]: 坐标点列表 [(x, y), ...]
        """
        t = np.linspace(0, 2 * np.pi, num_points)
        
        # 爱心参数方程
        x = 16 * np.sin(t) ** 3
        y = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
        
        # 翻转Y轴（因为屏幕坐标系Y向下为正）
        y = -y
        
        # 应用缩放
        x = x * self.scale / 16
        y = y * self.scale / 16
        
        # 转换为坐标点列表
        self.points = [(float(xi), float(yi)) for xi, yi in zip(x, y)]
        
        logger.debug(f"生成了 {len(self.points)} 个轨迹点")
        return self.points
    
    def get_point_at_progress(self, progress: float) -> Tuple[float, float]:
        """
        根据进度获取轨迹上的点
        
        Args:
            progress: 进度值 (0.0 到 1.0)
            
        Returns:
            Tuple[float, float]: (x, y) 坐标
        """
        if not self.points:
            self.generate_points()
        
        # 确保进度在有效范围内
        progress = progress % 1.0
        
        # 计算索引
        index = int(progress * len(self.points))
        index = min(index, len(self.points) - 1)
        
        x, y = self.points[index]
        
        # 添加中心偏移
        if self.center_x is not None and self.center_y is not None:
            x += self.center_x
            y += self.center_y
        
        return (x, y)
    
    def get_screen_center_position(self, screen_width: int, screen_height: int,
                                   offset_x: int = 0, offset_y: int = 0) -> Tuple[float, float]:
        """
        计算在屏幕中心的位置
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            offset_x: X轴偏移
            offset_y: Y轴偏移
            
        Returns:
            Tuple[float, float]: (center_x, center_y)
        """
        center_x = screen_width / 2 + offset_x
        center_y = screen_height / 2 + offset_y
        logger.debug(f"屏幕中心位置: ({center_x}, {center_y})")
        return (center_x, center_y)
    
    def set_center(self, center_x: float, center_y: float):
        """设置轨迹中心位置"""
        self.center_x = center_x
        self.center_y = center_y
        logger.debug(f"设置轨迹中心: ({center_x}, {center_y})")
    
    def get_random_offset_trajectory(self, max_offset: int = 200) -> 'HeartTrajectory':
        """
        创建一个带随机偏移的新轨迹
        
        Args:
            max_offset: 最大偏移距离
            
        Returns:
            HeartTrajectory: 新的轨迹对象
        """
        offset_x = np.random.randint(-max_offset, max_offset)
        offset_y = np.random.randint(-max_offset, max_offset)
        
        new_center_x = self.center_x + offset_x if self.center_x else offset_x
        new_center_y = self.center_y + offset_y if self.center_y else offset_y
        
        new_trajectory = HeartTrajectory(
            scale=self.scale,
            center_x=new_center_x,
            center_y=new_center_y
        )
        new_trajectory.generate_points()
        
        logger.debug(f"创建随机偏移轨迹: offset=({offset_x}, {offset_y})")
        return new_trajectory


if __name__ == '__main__':
    # 测试代码
    trajectory = HeartTrajectory(scale=100)
    trajectory.set_center(500, 400)
    
    # 生成轨迹点
    points = trajectory.generate_points(360)
    print(f"生成了 {len(points)} 个轨迹点")
    
    # 测试获取不同进度的点
    for progress in [0.0, 0.25, 0.5, 0.75, 1.0]:
        point = trajectory.get_point_at_progress(progress)
        print(f"进度 {progress}: 坐标 {point}")
