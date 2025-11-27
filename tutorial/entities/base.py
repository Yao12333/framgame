"""
实体基类模块 - 封装示例

【封装 (Encapsulation) 概念】
封装是面向对象编程的核心原则之一，它的目的是：
1. 隐藏内部实现细节
2. 保护数据不被随意修改
3. 提供清晰的公共接口

【Python 中的封装约定】
- _单下划线: 表示"受保护"的属性，约定不应从外部直接访问
- __双下划线: 名称改写(name mangling)，更强的私有性
- property: 提供受控的属性访问

【本模块演示】
1. 使用 _前缀 定义私有属性
2. 使用 @property 提供只读访问
3. 使用公共方法修改内部状态
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import uuid

# 尝试导入 pygame，如果不可用则使用模拟对象
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    # 创建模拟的 pygame.Rect 用于测试
    class MockRect:
        def __init__(self, x, y, w, h):
            self.x, self.y, self.width, self.height = x, y, w, h
            self.left, self.top = x, y
            self.right, self.bottom = x + w, y + h
        
        def colliderect(self, other):
            return not (self.right <= other.left or self.left >= other.right or
                       self.bottom <= other.top or self.top >= other.bottom)


class Entity(ABC):
    """
    游戏实体基类 - 所有游戏对象的父类
    
    【封装示例】
    这个类演示了如何正确封装数据：
    
    1. 私有属性（以 _ 开头）:
       - _id: 唯一标识符
       - _position: 位置坐标
       - _velocity: 速度向量
       - _size: 尺寸
       - _color: 颜色
       - _is_active: 是否激活
    
    2. 只读属性（通过 @property）:
       - id: 返回实体ID
       - position: 返回位置的副本（保护原始数据）
       - rect: 返回碰撞矩形
    
    3. 公共方法:
       - move(): 移动实体
       - update(): 更新状态（抽象方法）
       - render(): 渲染（抽象方法）
       - to_dict(): 序列化
       - from_dict(): 反序列化
    
    【为什么 position 返回副本？】
    如果直接返回 _position 的引用，外部代码可以这样修改：
        entity.position['x'] = 999  # 绕过了封装！
    
    返回副本后，修改副本不会影响原始数据：
        pos = entity.position
        pos['x'] = 999  # 只修改了副本，原始数据不变
    """
    
    def __init__(
        self,
        position: Tuple[float, float] = (0, 0),
        size: Tuple[int, int] = (32, 32),
        color: Tuple[int, int, int] = (255, 255, 255)
    ):
        """
        初始化实体
        
        【参数】
        - position: 初始位置 (x, y)
        - size: 尺寸 (宽, 高)
        - color: RGB 颜色 (r, g, b)
        
        【私有属性初始化】
        所有属性都以 _ 开头，表示它们是"私有"的
        """
        # 唯一标识符 - 使用 UUID 确保唯一性
        self._id: str = str(uuid.uuid4())
        
        # 位置 - 使用字典存储 x, y 坐标
        self._position: Dict[str, float] = {
            'x': float(position[0]),
            'y': float(position[1])
        }
        
        # 速度 - 每秒移动的像素数
        self._velocity: Dict[str, float] = {'x': 0.0, 'y': 0.0}
        
        # 尺寸 - 宽度和高度
        self._size: Tuple[int, int] = size
        
        # 颜色 - RGB 值
        self._color: Tuple[int, int, int] = color
        
        # 是否激活 - 非激活的实体不会更新和渲染
        self._is_active: bool = True
    
    # ==================== 只读属性 ====================
    
    @property
    def id(self) -> str:
        """
        获取实体ID（只读）
        
        【@property 装饰器】
        使方法可以像属性一样访问：
            entity.id  # 而不是 entity.id()
        """
        return self._id
    
    @property
    def position(self) -> Dict[str, float]:
        """
        获取位置（返回副本）
        
        【重要：返回副本而非引用】
        使用 .copy() 创建字典的浅拷贝
        这样外部修改返回值不会影响内部状态
        
        【示例】
        pos = entity.position  # 获取副本
        pos['x'] = 100  # 修改副本
        print(entity.position)  # 原始位置不变！
        """
        return self._position.copy()
    
    @property
    def velocity(self) -> Dict[str, float]:
        """获取速度（返回副本）"""
        return self._velocity.copy()
    
    @property
    def size(self) -> Tuple[int, int]:
        """获取尺寸（元组是不可变的，可以直接返回）"""
        return self._size
    
    @property
    def color(self) -> Tuple[int, int, int]:
        """获取颜色"""
        return self._color
    
    @property
    def is_active(self) -> bool:
        """获取激活状态"""
        return self._is_active
    
    @property
    def rect(self):
        """
        获取碰撞矩形
        
        【用途】
        用于碰撞检测，返回 pygame.Rect 对象
        """
        if PYGAME_AVAILABLE:
            return pygame.Rect(
                int(self._position['x']),
                int(self._position['y']),
                self._size[0],
                self._size[1]
            )
        else:
            return MockRect(
                int(self._position['x']),
                int(self._position['y']),
                self._size[0],
                self._size[1]
            )
    
    # ==================== 公共方法 ====================
    
    def move(self, dx: float, dy: float) -> None:
        """
        移动实体
        
        【参数】
        - dx: x 方向的位移
        - dy: y 方向的位移
        
        【为什么用方法而不是直接修改属性？】
        1. 可以在方法中添加验证逻辑（如边界检查）
        2. 可以触发事件（如位置改变通知）
        3. 便于调试和追踪状态变化
        """
        self._position['x'] += dx
        self._position['y'] += dy
    
    def set_velocity(self, vx: float, vy: float) -> None:
        """
        设置速度
        
        【参数】
        - vx: x 方向速度
        - vy: y 方向速度
        """
        self._velocity['x'] = vx
        self._velocity['y'] = vy
    
    def set_position(self, x: float, y: float) -> None:
        """
        设置位置
        
        【参数】
        - x: 新的 x 坐标
        - y: 新的 y 坐标
        """
        self._position['x'] = x
        self._position['y'] = y
    
    def activate(self) -> None:
        """激活实体"""
        self._is_active = True
    
    def deactivate(self) -> None:
        """停用实体"""
        self._is_active = False
    
    def _apply_velocity(self, delta_time: float) -> None:
        """
        应用速度更新位置（内部方法）
        
        【参数】
        - delta_time: 时间增量（秒）
        
        【物理公式】
        新位置 = 旧位置 + 速度 × 时间
        """
        self._position['x'] += self._velocity['x'] * delta_time
        self._position['y'] += self._velocity['y'] * delta_time
    
    # ==================== 抽象方法 ====================
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """
        更新实体状态（抽象方法）
        
        【抽象方法】
        使用 @abstractmethod 装饰器标记
        子类必须实现这个方法，否则无法实例化
        
        【参数】
        - delta_time: 上一帧到这一帧的时间（秒）
        """
        pass
    
    @abstractmethod
    def render(self, screen) -> None:
        """
        渲染实体（抽象方法）
        
        【参数】
        - screen: pygame 的 Surface 对象
        """
        pass
    
    # ==================== 序列化方法 ====================
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将实体转换为字典（序列化）
        
        【用途】
        1. 保存游戏状态
        2. 网络传输
        3. 调试输出
        
        【返回】
        包含实体所有状态的字典
        """
        return {
            'type': self.__class__.__name__,  # 类名，用于反序列化
            'id': self._id,
            'position': self._position.copy(),
            'velocity': self._velocity.copy(),
            'size': list(self._size),
            'color': list(self._color),
            'is_active': self._is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """
        从字典创建实体（反序列化）
        
        【类方法 @classmethod】
        - 第一个参数是类本身（cls），而不是实例（self）
        - 可以通过类直接调用：Entity.from_dict(data)
        - 子类调用时，cls 是子类
        
        【参数】
        - data: 包含实体状态的字典
        
        【返回】
        新创建的实体实例
        
        【注意】
        这是基类的实现，子类应该重写此方法以处理额外的属性
        """
        # 验证必要字段
        required_fields = ['position', 'size', 'color']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"缺少必要字段: {field}")
        
        # 这里不能直接实例化 Entity（因为是抽象类）
        # 子类会重写这个方法
        raise NotImplementedError("Entity 是抽象类，请使用具体子类的 from_dict")
    
    def __repr__(self) -> str:
        """
        返回实体的字符串表示（用于调试）
        """
        return (f"{self.__class__.__name__}("
                f"id={self._id[:8]}..., "
                f"pos=({self._position['x']:.1f}, {self._position['y']:.1f}), "
                f"active={self._is_active})")
