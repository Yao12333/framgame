"""
pygame 教学框架 - 主入口文件

【模块导入教学】
这个文件演示了如何组织和导入 Python 模块。

【导入方式】
1. 绝对导入: from tutorial.core.engine import GameEngine
2. 相对导入: from .core.engine import GameEngine (在包内使用)
3. 导入整个模块: import tutorial.core.engine as engine

【运行方式】
在项目根目录运行:
    python -m tutorial.main
或者:
    python tutorial/main.py

【学习路径】
1. 先看 entities/base.py - 学习封装
2. 再看 entities/player.py - 学习继承
3. 然后看 core/engine.py - 学习游戏循环
4. 最后看 core/resource_loader.py - 学习多线程
"""

import sys
import os
import random

# 确保可以导入 tutorial 包
# 这行代码将父目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== 模块导入示例 ====================

# 方式1: 从包中导入特定类
from tutorial.core.engine import GameEngine, check_collision
from tutorial.core.resource_loader import ResourceLoader
from tutorial.entities.player import Player
from tutorial.entities.collectible import Collectible, create_random_collectible
from tutorial.utils.event_bus import event_bus

# 方式2: 也可以这样导入整个模块
# from tutorial import core, entities, utils


def setup_event_listeners():
    """
    设置事件监听器
    
    【事件驱动编程】
    通过事件总线，不同模块可以解耦通信
    """
    def on_item_collected(data):
        """物品收集事件处理"""
        print(f"🌟 收集了 {data['points']} 分! 总分: {data['total_score']}")
    
    def on_game_started(data):
        """游戏开始事件处理"""
        print("🎮 游戏开始!")
        print("使用 WASD 或方向键移动，收集金色星星")
        print("按 ESC 退出")
    
    def on_game_ended(data):
        """游戏结束事件处理"""
        print(f"\n🏁 游戏结束! 最终得分: {data['score']}")
    
    # 订阅事件
    event_bus.subscribe('item_collected', on_item_collected)
    event_bus.subscribe('game_started', on_game_started)
    event_bus.subscribe('game_ended', on_game_ended)


def spawn_collectibles(engine: GameEngine, count: int = 5):
    """
    生成可收集物品
    
    【参数】
    - engine: 游戏引擎实例
    - count: 生成数量
    """
    for _ in range(count):
        collectible = create_random_collectible(
            screen_width=engine.width,
            screen_height=engine.height,
            margin=50
        )
        engine.add_entity(collectible)


def create_custom_update(engine: GameEngine):
    """
    创建自定义更新函数
    
    【闭包】
    这个函数返回一个闭包，可以访问 engine 变量
    """
    spawn_timer = 0.0
    spawn_interval = 3.0  # 每3秒生成新物品
    
    def custom_update(delta_time: float):
        nonlocal spawn_timer
        
        # 定时生成新物品
        spawn_timer += delta_time
        if spawn_timer >= spawn_interval:
            spawn_timer = 0.0
            
            # 检查当前活跃的收集物品数量
            active_collectibles = sum(
                1 for e in engine.get_entities()
                if isinstance(e, Collectible) and e.is_active
            )
            
            # 如果少于5个，生成新的
            if active_collectibles < 5:
                collectible = create_random_collectible(
                    screen_width=engine.width,
                    screen_height=engine.height
                )
                engine.add_entity(collectible)
    
    return custom_update


def main():
    """
    主函数 - 游戏入口
    
    【程序结构】
    1. 设置事件监听
    2. 创建游戏引擎
    3. 创建玩家
    4. 生成收集物品
    5. 运行游戏循环
    """
    print("=" * 50)
    print("  pygame 教学框架 - 弹球收集游戏")
    print("=" * 50)
    print()
    
    # 1. 设置事件监听
    setup_event_listeners()
    
    # 2. 创建游戏引擎
    engine = GameEngine(
        width=800,
        height=600,
        title="pygame 教学框架 - 收集游戏",
        fps=60
    )
    
    # 3. 创建玩家
    # 玩家初始位置在屏幕中央
    player = Player(
        position=(engine.width // 2 - 20, engine.height // 2 - 20),
        size=(40, 40),
        color=(0, 128, 255),  # 蓝色
        speed=250.0
    )
    engine.add_entity(player)
    
    # 4. 生成初始收集物品
    spawn_collectibles(engine, count=5)
    
    # 5. 设置自定义更新（定时生成新物品）
    engine.set_update_callback(create_custom_update(engine))
    
    # 6. 运行游戏
    print("\n正在启动游戏...")
    engine.run()
    
    print("\n感谢游玩!")


def demo_without_pygame():
    """
    无 pygame 的演示模式
    
    【用途】
    当没有安装 pygame 时，演示框架的核心功能
    """
    print("=" * 50)
    print("  pygame 教学框架 - 演示模式（无图形界面）")
    print("=" * 50)
    print()
    
    # 演示封装
    print("【封装示例】")
    player = Player(position=(100, 100), speed=200)
    print(f"玩家位置: {player.position}")
    
    # 尝试修改位置副本
    pos = player.position
    pos['x'] = 999
    print(f"修改副本后，玩家位置: {player.position}")
    print("  → 内部状态没有被修改（封装保护）")
    print()
    
    # 演示继承
    print("【继承示例】")
    print(f"Player 是 Entity 的子类: {Player.__bases__}")
    print(f"Collectible 是 Entity 的子类: {Collectible.__bases__}")
    print()
    
    # 演示序列化
    print("【序列化示例】")
    data = player.to_dict()
    print(f"序列化: {data}")
    restored = Player.from_dict(data)
    print(f"反序列化后位置: {restored.position}")
    print()
    
    # 演示碰撞检测
    print("【碰撞检测示例】")
    collectible = Collectible(position=(110, 110))
    collision = check_collision(player.rect, collectible.rect)
    print(f"玩家与物品碰撞: {collision}")
    
    collectible2 = Collectible(position=(500, 500))
    collision2 = check_collision(player.rect, collectible2.rect)
    print(f"玩家与远处物品碰撞: {collision2}")
    print()
    
    # 演示事件总线
    print("【事件总线示例】")
    
    def on_test_event(data):
        print(f"  收到事件: {data}")
    
    event_bus.subscribe('test', on_test_event)
    event_bus.emit('test', {'message': 'Hello from event bus!'})
    print()
    
    print("演示完成!")


if __name__ == "__main__":
    # 检查是否有 pygame
    try:
        import pygame
        main()
    except ImportError:
        print("未安装 pygame，运行演示模式")
        print("安装 pygame: pip install pygame")
        print()
        demo_without_pygame()
