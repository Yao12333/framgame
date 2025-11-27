"""
游戏引擎模块 - 游戏循环和核心管理

【游戏循环 (Game Loop) 概念】
游戏循环是游戏的心脏，它不断重复以下步骤：
1. 处理输入 (Handle Input)
2. 更新状态 (Update)
3. 渲染画面 (Render)

【帧率控制】
- FPS (Frames Per Second): 每秒渲染的帧数
- Delta Time: 上一帧到这一帧的时间间隔
- 使用 delta_time 确保游戏在不同帧率下行为一致

【本模块演示】
1. 游戏主循环的实现
2. 实体管理（添加、删除、更新）
3. 碰撞检测
4. 线程安全的实体列表操作
"""

import threading
from typing import List, Optional, Callable, Dict, Any
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from entities.base import Entity
from entities.player import Player
from entities.collectible import Collectible
from utils.event_bus import event_bus

# 尝试导入 pygame
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class GameEngine:
    """
    游戏引擎类 - 管理游戏循环和实体
    
    【封装示例】
    - 隐藏 pygame 初始化细节
    - 提供简洁的公共接口
    
    【线程安全】
    - 使用锁保护实体列表
    - 支持从其他线程安全地添加/删除实体
    
    【使用示例】
    ```python
    # 创建引擎
    engine = GameEngine(800, 600, "我的游戏")
    
    # 添加实体
    player = Player(position=(400, 300))
    engine.add_entity(player)
    
    # 运行游戏
    engine.run()
    ```
    """
    
    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        title: str = "Pygame Tutorial",
        fps: int = 60
    ):
        """
        初始化游戏引擎
        
        【参数】
        - width: 窗口宽度
        - height: 窗口高度
        - title: 窗口标题
        - fps: 目标帧率
        """
        self._width = width
        self._height = height
        self._title = title
        self._target_fps = fps
        
        # pygame 相关
        self._screen = None
        self._clock = None
        self._running = False
        self._initialized = False
        
        # 实体管理
        self._entities: List[Entity] = []
        self._entities_to_add: List[Entity] = []
        self._entities_to_remove: List[Entity] = []
        self._lock = threading.Lock()
        
        # 玩家引用（方便访问）
        self._player: Optional[Player] = None
        
        # 游戏状态
        self._score = 0
        self._delta_time = 0.0
        
        # 回调函数
        self._on_update: Optional[Callable[[float], None]] = None
        self._on_render: Optional[Callable, None] = None
    
    # ==================== 初始化和清理 ====================
    
    def initialize(self) -> bool:
        """
        初始化 pygame 和游戏窗口
        
        【返回】
        True 表示初始化成功，False 表示失败
        """
        if self._initialized:
            return True
        
        if not PYGAME_AVAILABLE:
            print("[GameEngine] pygame 不可用，以测试模式运行")
            self._initialized = True
            return True
        
        try:
            # 初始化 pygame
            pygame.init()
            
            # 创建窗口
            self._screen = pygame.display.set_mode((self._width, self._height))
            pygame.display.set_caption(self._title)
            
            # 创建时钟
            self._clock = pygame.time.Clock()
            
            self._initialized = True
            
            # 通知初始化完成
            event_bus.emit('engine_initialized', {
                'width': self._width,
                'height': self._height
            })
            
            return True
            
        except Exception as e:
            print(f"[GameEngine] 初始化失败: {e}")
            return False
    
    def cleanup(self) -> None:
        """
        清理资源
        """
        if PYGAME_AVAILABLE:
            pygame.quit()
        self._initialized = False
    
    # ==================== 实体管理 ====================
    
    def add_entity(self, entity: Entity) -> None:
        """
        添加实体到游戏
        
        【线程安全】
        使用锁保护，可以从任何线程调用
        
        【延迟添加】
        实体不会立即添加到列表，而是在下一帧开始时添加
        这避免了在遍历实体列表时修改它
        """
        with self._lock:
            self._entities_to_add.append(entity)
        
        # 如果是玩家，保存引用
        if isinstance(entity, Player):
            self._player = entity
    
    def remove_entity(self, entity: Entity) -> None:
        """
        从游戏中移除实体
        
        【线程安全】
        使用锁保护，可以从任何线程调用
        """
        with self._lock:
            self._entities_to_remove.append(entity)
    
    def get_entities(self) -> List[Entity]:
        """
        获取所有实体的副本
        
        【返回】
        实体列表的副本（避免外部修改）
        """
        with self._lock:
            return self._entities.copy()
    
    def get_player(self) -> Optional[Player]:
        """获取玩家实体"""
        return self._player
    
    def _process_entity_changes(self) -> None:
        """
        处理实体的添加和删除
        
        【内部方法】
        在每帧开始时调用，处理延迟的添加和删除操作
        """
        with self._lock:
            # 添加新实体
            for entity in self._entities_to_add:
                if entity not in self._entities:
                    self._entities.append(entity)
            self._entities_to_add.clear()
            
            # 删除实体
            for entity in self._entities_to_remove:
                if entity in self._entities:
                    self._entities.remove(entity)
            self._entities_to_remove.clear()
    
    # ==================== 游戏循环 ====================
    
    def run(self) -> None:
        """
        运行游戏主循环
        
        【游戏循环结构】
        ```
        while running:
            1. 处理实体变化
            2. 处理输入事件
            3. 更新游戏状态
            4. 检测碰撞
            5. 渲染画面
            6. 控制帧率
        ```
        """
        if not self.initialize():
            print("[GameEngine] 初始化失败，无法运行")
            return
        
        self._running = True
        
        # 通知游戏开始
        event_bus.emit('game_started', None)
        
        while self._running:
            # 计算 delta_time
            if PYGAME_AVAILABLE and self._clock:
                self._delta_time = self._clock.tick(self._target_fps) / 1000.0
            else:
                self._delta_time = 1.0 / self._target_fps
            
            # 1. 处理实体变化
            self._process_entity_changes()
            
            # 2. 处理输入
            self._handle_events()
            
            # 3. 更新状态
            self._update(self._delta_time)
            
            # 4. 检测碰撞
            self._check_collisions()
            
            # 5. 渲染
            self._render()
        
        # 清理
        self.cleanup()
        
        # 通知游戏结束
        event_bus.emit('game_ended', {'score': self._score})
    
    def stop(self) -> None:
        """停止游戏循环"""
        self._running = False
    
    def _handle_events(self) -> None:
        """
        处理输入事件
        
        【pygame 事件系统】
        pygame.event.get() 返回自上次调用以来的所有事件
        常见事件类型：
        - QUIT: 关闭窗口
        - KEYDOWN: 按键按下
        - KEYUP: 按键释放
        - MOUSEBUTTONDOWN: 鼠标按下
        """
        if not PYGAME_AVAILABLE:
            return
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            
            elif event.type == pygame.KEYDOWN:
                # 按键按下
                if event.key == pygame.K_ESCAPE:
                    self._running = False
                
                # 传递给玩家
                if self._player:
                    self._player.handle_key_down(event.key)
            
            elif event.type == pygame.KEYUP:
                # 按键释放
                if self._player:
                    self._player.handle_key_up(event.key)
    
    def _update(self, delta_time: float) -> None:
        """
        更新游戏状态
        
        【参数】
        - delta_time: 时间增量（秒）
        """
        # 更新所有实体
        with self._lock:
            for entity in self._entities:
                if entity.is_active:
                    entity.update(delta_time)
        
        # 调用自定义更新回调
        if self._on_update:
            self._on_update(delta_time)
    
    def _check_collisions(self) -> None:
        """
        检测碰撞
        
        【碰撞检测】
        检查玩家与所有可收集物品的碰撞
        使用 pygame.Rect.colliderect() 进行矩形碰撞检测
        """
        if not self._player or not self._player.is_active:
            return
        
        player_rect = self._player.rect
        
        with self._lock:
            for entity in self._entities:
                if isinstance(entity, Collectible) and entity.is_active:
                    if check_collision(player_rect, entity.rect):
                        # 收集物品
                        points = entity.collect()
                        self._player.add_score(points)
                        self._score = self._player.score
                        
                        # 通知收集事件
                        event_bus.emit('item_collected', {
                            'points': points,
                            'total_score': self._score
                        })
    
    def _render(self) -> None:
        """
        渲染画面
        """
        if not PYGAME_AVAILABLE or not self._screen:
            return
        
        # 清屏（深蓝色背景）
        self._screen.fill((20, 20, 40))
        
        # 渲染所有实体
        with self._lock:
            for entity in self._entities:
                if entity.is_active:
                    entity.render(self._screen)
        
        # 渲染 UI（分数）
        self._render_ui()
        
        # 调用自定义渲染回调
        if self._on_render:
            self._on_render()
        
        # 更新显示
        pygame.display.flip()
    
    def _render_ui(self) -> None:
        """
        渲染用户界面
        """
        if not PYGAME_AVAILABLE:
            return
        
        # 渲染分数
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self._score}", True, (255, 255, 255))
        self._screen.blit(score_text, (10, 10))
    
    # ==================== 回调设置 ====================
    
    def set_update_callback(self, callback: Callable[[float], None]) -> None:
        """设置自定义更新回调"""
        self._on_update = callback
    
    def set_render_callback(self, callback: Callable) -> None:
        """设置自定义渲染回调"""
        self._on_render = callback
    
    # ==================== 属性访问 ====================
    
    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    @property
    def score(self) -> int:
        return self._score
    
    @property
    def delta_time(self) -> float:
        return self._delta_time
    
    @property
    def is_running(self) -> bool:
        return self._running


# ==================== 碰撞检测函数 ====================

def check_collision(rect1, rect2) -> bool:
    """
    检测两个矩形是否碰撞
    
    【参数】
    - rect1: 第一个矩形（pygame.Rect 或类似对象）
    - rect2: 第二个矩形
    
    【返回】
    True 表示碰撞，False 表示不碰撞
    
    【算法】
    两个矩形碰撞当且仅当它们在 X 和 Y 方向上都有重叠
    """
    if PYGAME_AVAILABLE and hasattr(rect1, 'colliderect'):
        return rect1.colliderect(rect2)
    
    # 手动实现碰撞检测（用于测试）
    return not (
        rect1.right <= rect2.left or
        rect1.left >= rect2.right or
        rect1.bottom <= rect2.top or
        rect1.top >= rect2.bottom
    )


# 全局引擎实例（可选使用）
game_engine: Optional[GameEngine] = None


def create_engine(width: int = 800, height: int = 600, title: str = "Pygame Tutorial") -> GameEngine:
    """
    创建游戏引擎实例
    
    【工厂函数】
    提供一个简单的方式创建和获取引擎实例
    """
    global game_engine
    game_engine = GameEngine(width, height, title)
    return game_engine
