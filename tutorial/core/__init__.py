"""
核心模块包

包含游戏引擎和资源加载器等核心组件。

【学习要点】
1. 子包也需要 __init__.py
2. 可以在这里导入子模块，简化外部导入路径
"""

# 当核心模块实现后，可以这样导出：
# from .engine import GameEngine
# from .resource_loader import ResourceLoader

__all__ = ['engine', 'resource_loader']
