"""
实体模块包

包含所有游戏实体类：基类、玩家、可收集物品等。

【学习要点】
1. 实体是游戏中的"对象"，如玩家、敌人、道具
2. 使用继承来复用代码
3. 通过 __init__.py 可以简化导入路径
"""

# 当实体类实现后，可以这样导出：
# from .base import Entity
# from .player import Player
# from .collectible import Collectible

__all__ = ['base', 'player', 'collectible']
