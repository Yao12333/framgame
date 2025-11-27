"""
工具模块包

包含辅助工具类，如事件总线。

【学习要点】
1. 工具类通常是独立的、可复用的组件
2. 事件总线用于模块间解耦通信
"""

# 当工具类实现后，可以这样导出：
# from .event_bus import EventBus, event_bus

__all__ = ['event_bus']
