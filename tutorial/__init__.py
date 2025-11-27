"""
pygame 教学框架主包

这个包演示了如何组织一个 Python 游戏项目。
通过 __init__.py 文件，我们可以控制哪些模块对外可见。

【学习要点】
1. __init__.py 使目录成为 Python 包
2. 可以在这里定义包级别的导出
3. 使用 __all__ 控制 from package import * 的行为
"""

# 版本信息
__version__ = "1.0.0"
__author__ = "Tutorial"

# 定义公开的模块（当使用 from tutorial import * 时导入这些）
__all__ = ['core', 'entities', 'utils']
