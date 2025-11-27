"""
资源加载器模块 - 多线程示例

【多线程 (Multithreading) 概念】
多线程允许程序同时执行多个任务。在游戏中，常见用途包括：
1. 后台加载资源（不阻塞游戏画面）
2. 网络通信
3. AI 计算

【Python 多线程注意事项】
1. GIL (Global Interpreter Lock): Python 的 GIL 限制了 CPU 密集型任务的并行
2. 适用场景: I/O 密集型任务（如文件读取、网络请求）
3. 线程安全: 多线程访问共享数据需要使用锁

【本模块演示】
1. 使用 threading.Thread 创建后台线程
2. 使用 threading.Lock 保护共享数据
3. 线程间通信（通过事件总线）
"""

import threading
import time
import os
from typing import Dict, Any, List, Optional, Callable

# 导入事件总线用于通知
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.event_bus import event_bus

# 尝试导入 pygame
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class ResourceLoader:
    """
    资源加载器 - 多线程异步加载资源
    
    【多线程示例】
    这个类演示了如何在后台线程中加载资源，
    同时保持主线程（游戏循环）的流畅运行。
    
    【线程安全】
    - _resources: 使用锁保护的共享字典
    - _progress: 使用锁保护的进度值
    - _is_loading: 使用锁保护的状态标志
    
    【使用示例】
    ```python
    loader = ResourceLoader()
    
    # 定义要加载的资源
    resources = [
        {'name': 'player', 'path': 'assets/player.png', 'type': 'image'},
        {'name': 'coin', 'path': 'assets/coin.wav', 'type': 'sound'},
    ]
    
    # 开始异步加载
    loader.load_async(resources)
    
    # 在游戏循环中检查加载状态
    while loader.is_loading():
        print(f"加载进度: {loader.get_progress():.0%}")
        # 可以显示加载画面
    
    # 加载完成后获取资源
    player_img = loader.get_resource('player')
    ```
    """
    
    def __init__(self):
        """
        初始化资源加载器
        
        【私有属性】
        - _resources: 已加载的资源字典
        - _lock: 线程锁
        - _loading_thread: 加载线程
        - _is_loading: 是否正在加载
        - _progress: 加载进度 (0.0 - 1.0)
        - _total_items: 总资源数
        - _loaded_items: 已加载资源数
        """
        # 已加载的资源
        self._resources: Dict[str, Any] = {}
        
        # 线程锁 - 保护共享数据
        # 当多个线程需要访问同一数据时，使用锁确保同一时间只有一个线程能访问
        self._lock = threading.Lock()
        
        # 加载线程
        self._loading_thread: Optional[threading.Thread] = None
        
        # 加载状态
        self._is_loading: bool = False
        self._progress: float = 0.0
        self._total_items: int = 0
        self._loaded_items: int = 0
        
        # 错误信息
        self._errors: List[str] = []
    
    def load_async(self, resource_list: List[Dict[str, str]], 
                   on_complete: Optional[Callable] = None) -> None:
        """
        异步加载资源列表
        
        【参数】
        - resource_list: 资源列表，每个资源是一个字典：
            {'name': '资源名', 'path': '文件路径', 'type': '类型'}
        - on_complete: 加载完成后的回调函数（可选）
        
        【资源类型】
        - 'image': 图片文件
        - 'sound': 音效文件
        - 'font': 字体文件
        
        【线程创建】
        使用 threading.Thread 创建新线程
        - target: 线程要执行的函数
        - args: 传递给函数的参数
        - daemon=True: 守护线程，主程序退出时自动结束
        """
        # 如果已经在加载，先等待完成
        if self._is_loading:
            print("[ResourceLoader] 警告: 已有加载任务在进行中")
            return
        
        # 重置状态
        with self._lock:
            self._is_loading = True
            self._progress = 0.0
            self._total_items = len(resource_list)
            self._loaded_items = 0
            self._errors.clear()
        
        # 创建并启动加载线程
        self._loading_thread = threading.Thread(
            target=self._load_resources_thread,
            args=(resource_list, on_complete),
            daemon=True  # 守护线程
        )
        self._loading_thread.start()
        
        # 通过事件总线通知加载开始
        event_bus.emit('resource_loading_started', {
            'total': self._total_items
        })
    
    def _load_resources_thread(self, resource_list: List[Dict[str, str]],
                                on_complete: Optional[Callable]) -> None:
        """
        加载线程的主函数（在后台线程中执行）
        
        【注意】
        这个方法在单独的线程中运行，
        访问共享数据时必须使用锁！
        """
        for i, resource in enumerate(resource_list):
            try:
                name = resource.get('name', f'resource_{i}')
                path = resource.get('path', '')
                res_type = resource.get('type', 'unknown')
                
                # 加载资源
                loaded_resource = self._load_single_resource(path, res_type)
                
                # 使用锁保护共享数据的写入
                with self._lock:
                    self._resources[name] = loaded_resource
                    self._loaded_items += 1
                    self._progress = self._loaded_items / self._total_items
                
                # 通知单个资源加载完成
                event_bus.emit('resource_loaded', {
                    'name': name,
                    'progress': self._progress
                })
                
            except Exception as e:
                error_msg = f"加载 {resource.get('name', 'unknown')} 失败: {e}"
                with self._lock:
                    self._errors.append(error_msg)
                print(f"[ResourceLoader] {error_msg}")
        
        # 加载完成
        with self._lock:
            self._is_loading = False
            self._progress = 1.0
        
        # 通知加载完成
        event_bus.emit('resource_loading_complete', {
            'total': self._total_items,
            'errors': len(self._errors)
        })
        
        # 调用完成回调
        if on_complete:
            try:
                on_complete()
            except Exception as e:
                print(f"[ResourceLoader] 回调执行错误: {e}")
    
    def _load_single_resource(self, path: str, res_type: str) -> Any:
        """
        加载单个资源
        
        【参数】
        - path: 文件路径
        - res_type: 资源类型
        
        【返回】
        加载的资源对象
        """
        # 模拟加载延迟（实际项目中删除这行）
        time.sleep(0.1)
        
        if not PYGAME_AVAILABLE:
            # 没有 pygame 时返回占位符
            return {'type': res_type, 'path': path, 'loaded': True}
        
        if res_type == 'image':
            # 加载图片
            if os.path.exists(path):
                return pygame.image.load(path).convert_alpha()
            else:
                # 创建占位符图片
                surface = pygame.Surface((32, 32))
                surface.fill((255, 0, 255))  # 紫色表示缺失
                return surface
        
        elif res_type == 'sound':
            # 加载音效
            if os.path.exists(path):
                return pygame.mixer.Sound(path)
            else:
                return None
        
        elif res_type == 'font':
            # 加载字体
            size = 24  # 默认大小
            if os.path.exists(path):
                return pygame.font.Font(path, size)
            else:
                return pygame.font.Font(None, size)  # 使用默认字体
        
        else:
            # 未知类型，返回原始数据
            return {'type': res_type, 'path': path}
    
    def get_resource(self, name: str) -> Optional[Any]:
        """
        获取已加载的资源
        
        【参数】
        - name: 资源名称
        
        【返回】
        资源对象，如果不存在返回 None
        
        【线程安全】
        使用锁保护读取操作
        """
        with self._lock:
            return self._resources.get(name)
    
    def is_loading(self) -> bool:
        """
        检查是否正在加载
        
        【返回】
        True 表示正在加载，False 表示加载完成或未开始
        """
        with self._lock:
            return self._is_loading
    
    def get_progress(self) -> float:
        """
        获取加载进度
        
        【返回】
        0.0 到 1.0 之间的浮点数
        """
        with self._lock:
            return self._progress
    
    def get_errors(self) -> List[str]:
        """
        获取加载错误列表
        
        【返回】
        错误信息列表
        """
        with self._lock:
            return self._errors.copy()
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """
        等待加载完成（阻塞当前线程）
        
        【参数】
        - timeout: 超时时间（秒），None 表示无限等待
        
        【返回】
        True 表示加载完成，False 表示超时
        
        【注意】
        这个方法会阻塞调用线程，通常只在初始化时使用
        """
        if self._loading_thread:
            self._loading_thread.join(timeout)
            return not self._loading_thread.is_alive()
        return True
    
    def clear(self) -> None:
        """
        清除所有已加载的资源
        """
        with self._lock:
            self._resources.clear()
            self._errors.clear()


# 全局资源加载器实例
resource_loader = ResourceLoader()
