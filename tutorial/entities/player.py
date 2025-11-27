"""
玩家类模块 - 继承示例

【继承 (Inheritance) 概念】
继承是面向对象编程的核心原则之一，它允许：
1. 代码复用：子类自动获得父类的属性和方法
2. 扩展功能：子类可以添加新的属性和方法
3. 方法重写：子类可以修改父类的行为

【本模块演示】
1. Player 继承自 Entity 基类
2. 添加玩家特有的属性（分数、速度）
3. 重写 update() 方法处理键盘输入
4. 使用 super() 调用父类方法
"""

from typing import Dict, Any, Tuple, Set
from .base import Entity, PYGAME_AVAILABLE

if PYGAME_AVAILABLE:
    import pygame


class Player(Entity):
    """
    玩家类 - 继承自 Entity
    
    【继承示例】
    Player 继承了 Entity 的所有功能：
    - 位置、速度、尺寸、颜色等属性
    - move()、set_velocity() 等方法
    - to_dict()、from_dict() 序列化方法
    
    Player 添加了自己的功能：
    - _score: 玩家分数
    - _speed: 移动速度
    - 键盘输入处理
    
    【使用示例】
    ```python
    # 创建玩家
    player = Player(position=(100, 100), speed=200)
    
    # 游戏循环中
    player.update(delta_time)  # 处理输入并移动
    player.render(screen)      # 渲染玩家
    
    # 得分
    player.add_score(10)
    print(f"当前分数: {player.score}")
    ```
    """
    
    def __init__(
        self,
        position: Tuple[float, float] = (0, 0),
        size: Tuple[int, int] = (40, 40),
        color: Tuple[int, int, int] = (0, 128, 255),  # 蓝色
        speed: float = 200.0
    ):
        """
        初始化玩家
        
        【参数】
        - position: 初始位置
        - size: 玩家尺寸
        - color: 玩家颜色
        - speed: 移动速度（像素/秒）
        
        【super() 的使用】
        super().__init__() 调用父类的构造函数
        这确保父类的初始化逻辑被执行
        """
        # 调用父类构造函数
        # 这是继承中非常重要的一步！
        super().__init__(position=position, size=size, color=color)
        
        # 玩家特有的属性
        self._score: int = 0
        self._speed: float = speed
        
        # 当前按下的键（用于平滑移动）
        self._pressed_keys: Set[int] = set()
    
    # ==================== 玩家特有的属性 ====================
    
    @property
    def score(self) -> int:
        """获取当前分数"""
        return self._score
    
    @property
    def speed(self) -> float:
        """获取移动速度"""
        return self._speed
    
    # ==================== 玩家特有的方法 ====================
    
    def add_score(self, points: int) -> None:
        """
        增加分数
        
        【参数】
        - points: 要增加的分数
        """
        self._score += points
    
    def reset_score(self) -> None:
        """重置分数为 0"""
        self._score = 0
    
    def handle_key_down(self, key: int) -> None:
        """
        处理按键按下事件
        
        【参数】
        - key: pygame 键码
        """
        self._pressed_keys.add(key)
    
    def handle_key_up(self, key: int) -> None:
        """
        处理按键释放事件
        
        【参数】
        - key: pygame 键码
        """
        self._pressed_keys.discard(key)
    
    # ==================== 重写父类方法 ====================
    
    def update(self, delta_time: float) -> None:
        """
        更新玩家状态（重写父类方法）
        
        【方法重写 (Method Override)】
        子类可以重新定义父类的方法，提供不同的实现。
        这里我们重写 update() 来添加键盘输入处理。
        
        【参数】
        - delta_time: 时间增量（秒）
        
        【实现逻辑】
        1. 根据按下的键计算移动方向
        2. 设置速度
        3. 应用速度更新位置
        """
        if not self._is_active:
            return
        
        # 计算移动方向
        dx, dy = 0, 0
        
        # 使用 pygame.key.get_pressed() 获取当前按键状态
        # 这比事件驱动更可靠
        if PYGAME_AVAILABLE:
            import pygame
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += 1
        else:
            # 测试模式：使用 _pressed_keys
            if 1073741904 in self._pressed_keys or 97 in self._pressed_keys:
                dx -= 1
            if 1073741903 in self._pressed_keys or 100 in self._pressed_keys:
                dx += 1
            if 1073741906 in self._pressed_keys or 119 in self._pressed_keys:
                dy -= 1
            if 1073741905 in self._pressed_keys or 115 in self._pressed_keys:
                dy += 1
        
        # 设置速度
        self._velocity['x'] = dx * self._speed
        self._velocity['y'] = dy * self._speed
        
        # 应用速度更新位置（调用父类的内部方法）
        self._apply_velocity(delta_time)
    
    def render(self, screen) -> None:
        """
        渲染玩家（重写父类方法）
        
        【参数】
        - screen: pygame Surface 对象
        """
        if not self._is_active:
            return
        
        if PYGAME_AVAILABLE:
            # 绘制玩家矩形
            pygame.draw.rect(screen, self._color, self.rect)
            
            # 绘制边框
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
    
    # ==================== 序列化方法 ====================
    
    def to_dict(self) -> Dict[str, Any]:
        """
        序列化玩家（扩展父类方法）
        
        【super() 的使用】
        先调用父类的 to_dict() 获取基础数据，
        然后添加玩家特有的数据。
        """
        # 获取父类的序列化数据
        data = super().to_dict()
        
        # 添加玩家特有的数据
        data['score'] = self._score
        data['speed'] = self._speed
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """
        从字典创建玩家（重写父类方法）
        
        【类方法继承】
        子类的 from_dict 需要处理子类特有的属性
        """
        # 提取基础属性
        position = (data['position']['x'], data['position']['y'])
        size = tuple(data['size'])
        color = tuple(data['color'])
        speed = data.get('speed', 200.0)
        
        # 创建玩家实例
        player = cls(position=position, size=size, color=color, speed=speed)
        
        # 恢复其他属性
        if 'id' in data:
            player._id = data['id']
        if 'velocity' in data:
            player._velocity = data['velocity'].copy()
        if 'is_active' in data:
            player._is_active = data['is_active']
        if 'score' in data:
            player._score = data['score']
        
        return player
