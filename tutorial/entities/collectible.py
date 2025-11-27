"""
可收集物品类模块 - 继承示例

【继承的另一个示例】
Collectible 也继承自 Entity，展示了：
1. 同一个父类可以有多个不同的子类
2. 每个子类可以有自己独特的行为
3. 多态：不同子类可以用相同的接口操作

【本模块演示】
1. Collectible 继承自 Entity
2. 添加收集物品特有的属性（分值）
3. 实现收集逻辑
4. 可选的动画效果
"""

import math
import random
from typing import Dict, Any, Tuple
from .base import Entity, PYGAME_AVAILABLE

if PYGAME_AVAILABLE:
    import pygame


class Collectible(Entity):
    """
    可收集物品类 - 继承自 Entity
    
    【继承示例】
    Collectible 和 Player 都继承自 Entity，
    但它们有不同的行为：
    - Player: 响应键盘输入移动
    - Collectible: 静止或有简单动画，可被收集
    
    【多态 (Polymorphism)】
    因为 Player 和 Collectible 都是 Entity 的子类，
    游戏引擎可以用统一的方式处理它们：
    ```python
    for entity in entities:
        entity.update(delta_time)  # 多态调用
        entity.render(screen)
    ```
    
    【使用示例】
    ```python
    # 创建星星
    star = Collectible(position=(200, 150), points=10)
    
    # 检测碰撞并收集
    if player.rect.colliderect(star.rect):
        points = star.collect()
        player.add_score(points)
    ```
    """
    
    def __init__(
        self,
        position: Tuple[float, float] = (0, 0),
        size: Tuple[int, int] = (24, 24),
        color: Tuple[int, int, int] = (255, 215, 0),  # 金色
        points: int = 10
    ):
        """
        初始化可收集物品
        
        【参数】
        - position: 位置
        - size: 尺寸
        - color: 颜色（默认金色）
        - points: 收集后获得的分数
        """
        super().__init__(position=position, size=size, color=color)
        
        # 收集物品特有的属性
        self._points: int = points
        
        # 动画相关
        self._animation_time: float = 0.0
        self._base_y: float = position[1]  # 记录初始 Y 坐标用于浮动动画
    
    # ==================== 收集物品特有的属性 ====================
    
    @property
    def points(self) -> int:
        """获取分值"""
        return self._points
    
    # ==================== 收集物品特有的方法 ====================
    
    def collect(self) -> int:
        """
        收集物品
        
        【返回】
        - 收集获得的分数
        
        【行为】
        1. 停用物品（不再更新和渲染）
        2. 返回分值
        """
        if not self._is_active:
            return 0
        
        # 停用物品
        self.deactivate()
        
        return self._points
    
    def respawn(self, position: Tuple[float, float]) -> None:
        """
        重新生成物品
        
        【参数】
        - position: 新的位置
        """
        self.set_position(position[0], position[1])
        self._base_y = position[1]
        self._animation_time = random.uniform(0, 2 * math.pi)  # 随机起始相位
        self.activate()
    
    # ==================== 重写父类方法 ====================
    
    def update(self, delta_time: float) -> None:
        """
        更新物品状态（重写父类方法）
        
        【实现】
        添加简单的浮动动画效果
        """
        if not self._is_active:
            return
        
        # 更新动画时间
        self._animation_time += delta_time * 3  # 动画速度
        
        # 浮动动画：上下移动
        # 使用正弦函数创建平滑的上下浮动
        float_offset = math.sin(self._animation_time) * 5  # 振幅 5 像素
        self._position['y'] = self._base_y + float_offset
    
    def render(self, screen) -> None:
        """
        渲染物品（重写父类方法）
        
        【实现】
        绘制一个简单的星星形状
        """
        if not self._is_active:
            return
        
        if PYGAME_AVAILABLE:
            # 获取中心点
            cx = int(self._position['x'] + self._size[0] / 2)
            cy = int(self._position['y'] + self._size[1] / 2)
            radius = min(self._size) // 2
            
            # 绘制星星（简化为圆形）
            pygame.draw.circle(screen, self._color, (cx, cy), radius)
            
            # 绘制高光效果
            highlight_color = (255, 255, 200)
            pygame.draw.circle(screen, highlight_color, (cx - 2, cy - 2), radius // 3)
    
    # ==================== 序列化方法 ====================
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化物品"""
        data = super().to_dict()
        data['points'] = self._points
        data['base_y'] = self._base_y
        data['animation_time'] = self._animation_time
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Collectible':
        """从字典创建物品"""
        position = (data['position']['x'], data['position']['y'])
        size = tuple(data['size'])
        color = tuple(data['color'])
        points = data.get('points', 10)
        
        collectible = cls(position=position, size=size, color=color, points=points)
        
        if 'id' in data:
            collectible._id = data['id']
        if 'velocity' in data:
            collectible._velocity = data['velocity'].copy()
        if 'is_active' in data:
            collectible._is_active = data['is_active']
        if 'base_y' in data:
            collectible._base_y = data['base_y']
        if 'animation_time' in data:
            collectible._animation_time = data['animation_time']
        
        return collectible


# ==================== 工厂函数 ====================

def create_random_collectible(
    screen_width: int = 800,
    screen_height: int = 600,
    margin: int = 50
) -> Collectible:
    """
    创建随机位置的收集物品
    
    【工厂函数】
    这是一个辅助函数，用于方便地创建随机位置的物品
    
    【参数】
    - screen_width: 屏幕宽度
    - screen_height: 屏幕高度
    - margin: 边距（物品不会生成在边缘）
    
    【返回】
    - 新创建的 Collectible 实例
    """
    x = random.randint(margin, screen_width - margin)
    y = random.randint(margin, screen_height - margin)
    
    # 随机分值（10-50）
    points = random.choice([10, 20, 30, 50])
    
    # 根据分值设置颜色
    colors = {
        10: (255, 215, 0),    # 金色
        20: (192, 192, 192),  # 银色
        30: (255, 165, 0),    # 橙色
        50: (255, 0, 255),    # 紫色（稀有）
    }
    
    return Collectible(
        position=(x, y),
        color=colors.get(points, (255, 215, 0)),
        points=points
    )
