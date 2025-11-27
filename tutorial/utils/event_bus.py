"""
事件总线模块 - 观察者模式示例

【设计模式：观察者模式 (Observer Pattern)】
观察者模式定义了对象之间的一对多依赖关系，当一个对象状态改变时，
所有依赖它的对象都会收到通知并自动更新。

【使用场景】
- 模块间解耦通信（如：资源加载完成通知游戏引擎）
- 事件驱动编程（如：玩家得分时更新 UI）

【线程安全】
使用 threading.Lock 保护共享数据，确保多线程环境下的安全性。
"""

import threading
from typing import Callable, Any, Dict, List


class EventBus:
    """
    事件总线类 - 实现发布/订阅模式
    
    【封装要点】
    1. _listeners 是私有属性，外部不能直接访问
    2. _lock 保护多线程访问
    3. 只通过公共方法操作内部状态
    
    【使用示例】
    ```python
    # 创建事件总线
    bus = EventBus()
    
    # 订阅事件
    def on_score_change(score):
        print(f"分数变化: {score}")
    
    bus.subscribe("score_changed", on_score_change)
    
    # 发布事件
    bus.emit("score_changed", 100)  # 输出: 分数变化: 100
    
    # 取消订阅
    bus.unsubscribe("score_changed", on_score_change)
    ```
    """
    
    def __init__(self):
        """
        初始化事件总线
        
        【私有属性说明】
        - _listeners: 存储事件名到回调函数列表的映射
        - _lock: 线程锁，保护 _listeners 的并发访问
        """
        # 私有属性：事件监听器字典
        # 结构: {"事件名": [回调函数1, 回调函数2, ...]}
        self._listeners: Dict[str, List[Callable]] = {}
        
        # 私有属性：线程锁
        # 用于保护 _listeners 在多线程环境下的安全访问
        self._lock = threading.Lock()
    
    def subscribe(self, event: str, callback: Callable) -> None:
        """
        订阅事件
        
        【参数】
        - event: 事件名称（字符串）
        - callback: 回调函数，当事件触发时被调用
        
        【线程安全】
        使用 with self._lock 确保添加监听器时的线程安全
        """
        # with 语句自动获取和释放锁
        # 这是 Python 推荐的锁使用方式，确保异常时也能释放锁
        with self._lock:
            # 如果事件不存在，创建空列表
            if event not in self._listeners:
                self._listeners[event] = []
            
            # 避免重复订阅同一个回调
            if callback not in self._listeners[event]:
                self._listeners[event].append(callback)
    
    def unsubscribe(self, event: str, callback: Callable) -> None:
        """
        取消订阅事件
        
        【参数】
        - event: 事件名称
        - callback: 要移除的回调函数
        """
        with self._lock:
            if event in self._listeners:
                # 使用 try-except 处理回调不存在的情况
                try:
                    self._listeners[event].remove(callback)
                except ValueError:
                    # 回调不在列表中，忽略
                    pass
    
    def emit(self, event: str, data: Any = None) -> None:
        """
        发布/触发事件
        
        【参数】
        - event: 事件名称
        - data: 传递给回调函数的数据（可选）
        
        【实现细节】
        1. 先复制监听器列表，避免在遍历时修改
        2. 在锁外调用回调，避免死锁
        """
        # 在锁内复制监听器列表
        with self._lock:
            # 使用 .get() 方法安全获取，不存在时返回空列表
            # 使用 list() 创建副本，避免遍历时被修改
            callbacks = list(self._listeners.get(event, []))
        
        # 在锁外调用回调函数
        # 这样做是为了：
        # 1. 避免回调函数执行时间过长导致锁被长时间持有
        # 2. 避免回调函数中再次调用 emit 导致死锁
        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                # 捕获回调中的异常，避免影响其他监听器
                print(f"[EventBus] 回调执行错误: {e}")
    
    def clear(self, event: str = None) -> None:
        """
        清除事件监听器
        
        【参数】
        - event: 要清除的事件名。如果为 None，清除所有事件
        """
        with self._lock:
            if event is None:
                # 清除所有监听器
                self._listeners.clear()
            elif event in self._listeners:
                # 清除指定事件的监听器
                del self._listeners[event]
    
    def has_listeners(self, event: str) -> bool:
        """
        检查事件是否有监听器
        
        【返回】
        - True: 事件有至少一个监听器
        - False: 事件没有监听器
        """
        with self._lock:
            return event in self._listeners and len(self._listeners[event]) > 0


# 全局事件总线实例（单例模式的简化实现）
# 这样其他模块可以直接导入使用，无需自己创建实例
# 使用方式: from tutorial.utils.event_bus import event_bus
event_bus = EventBus()
