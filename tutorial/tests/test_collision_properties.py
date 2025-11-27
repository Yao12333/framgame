"""
碰撞检测属性测试模块

测试碰撞检测的正确性
"""

import pytest
from hypothesis import given, strategies as st, settings, assume

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tutorial.core.engine import check_collision
from tutorial.entities.player import Player
from tutorial.entities.collectible import Collectible


# 模拟 Rect 类用于测试
class MockRect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.left = x
        self.top = y
        self.right = x + w
        self.bottom = y + h


class TestCollisionDetection:
    """
    **Feature: pygame-tutorial-framework, Property 4: 碰撞检测正确性**
    
    **Validates: Requirements 5.4**
    
    测试：对于任意两个 Entity 实例，碰撞检测结果应该与它们的矩形区域是否重叠一致。
    """
    
    @given(
        x1=st.integers(min_value=0, max_value=700),
        y1=st.integers(min_value=0, max_value=500),
        w1=st.integers(min_value=10, max_value=100),
        h1=st.integers(min_value=10, max_value=100),
        x2=st.integers(min_value=0, max_value=700),
        y2=st.integers(min_value=0, max_value=500),
        w2=st.integers(min_value=10, max_value=100),
        h2=st.integers(min_value=10, max_value=100)
    )
    @settings(max_examples=100)
    def test_collision_detection_correctness(
        self, x1: int, y1: int, w1: int, h1: int,
        x2: int, y2: int, w2: int, h2: int
    ):
        """
        属性测试：碰撞检测与矩形重叠一致
        
        【测试逻辑】
        1. 创建两个矩形
        2. 手动计算是否重叠
        3. 验证 check_collision 返回相同结果
        """
        rect1 = MockRect(x1, y1, w1, h1)
        rect2 = MockRect(x2, y2, w2, h2)
        
        # 手动计算是否重叠
        # 两个矩形重叠当且仅当它们在 X 和 Y 方向上都有重叠
        x_overlap = not (rect1.right <= rect2.left or rect1.left >= rect2.right)
        y_overlap = not (rect1.bottom <= rect2.top or rect1.top >= rect2.bottom)
        expected_collision = x_overlap and y_overlap
        
        # 验证 check_collision 结果
        actual_collision = check_collision(rect1, rect2)
        
        assert actual_collision == expected_collision, \
            f"碰撞检测错误: rect1=({x1},{y1},{w1},{h1}), rect2=({x2},{y2},{w2},{h2}), " \
            f"期望={expected_collision}, 实际={actual_collision}"
    
    @given(
        x=st.integers(min_value=0, max_value=700),
        y=st.integers(min_value=0, max_value=500),
        w=st.integers(min_value=10, max_value=100),
        h=st.integers(min_value=10, max_value=100)
    )
    @settings(max_examples=100)
    def test_collision_with_self(self, x: int, y: int, w: int, h: int):
        """
        属性测试：矩形与自身总是碰撞
        """
        rect = MockRect(x, y, w, h)
        assert check_collision(rect, rect), "矩形应该与自身碰撞"
    
    @given(
        x1=st.integers(min_value=0, max_value=300),
        y1=st.integers(min_value=0, max_value=300),
        w=st.integers(min_value=10, max_value=50),
        h=st.integers(min_value=10, max_value=50),
        gap=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=100)
    def test_no_collision_when_separated(self, x1: int, y1: int, w: int, h: int, gap: int):
        """
        属性测试：分离的矩形不碰撞
        """
        rect1 = MockRect(x1, y1, w, h)
        # rect2 在 rect1 右边，有间隙
        rect2 = MockRect(x1 + w + gap, y1, w, h)
        
        assert not check_collision(rect1, rect2), "分离的矩形不应该碰撞"
    
    @given(
        x1=st.integers(min_value=100, max_value=600),
        y1=st.integers(min_value=100, max_value=400),
        w1=st.integers(min_value=30, max_value=80),
        h1=st.integers(min_value=30, max_value=80),
        offset_x=st.integers(min_value=-20, max_value=20),
        offset_y=st.integers(min_value=-20, max_value=20)
    )
    @settings(max_examples=100)
    def test_collision_is_symmetric(
        self, x1: int, y1: int, w1: int, h1: int, offset_x: int, offset_y: int
    ):
        """
        属性测试：碰撞检测是对称的
        
        check_collision(A, B) == check_collision(B, A)
        """
        rect1 = MockRect(x1, y1, w1, h1)
        rect2 = MockRect(x1 + offset_x, y1 + offset_y, w1, h1)
        
        collision_1_2 = check_collision(rect1, rect2)
        collision_2_1 = check_collision(rect2, rect1)
        
        assert collision_1_2 == collision_2_1, "碰撞检测应该是对称的"


class TestEntityCollision:
    """
    测试实际 Entity 对象之间的碰撞
    """
    
    @given(
        x1=st.floats(min_value=0, max_value=700, allow_nan=False, allow_infinity=False),
        y1=st.floats(min_value=0, max_value=500, allow_nan=False, allow_infinity=False),
        x2=st.floats(min_value=0, max_value=700, allow_nan=False, allow_infinity=False),
        y2=st.floats(min_value=0, max_value=500, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_player_collectible_collision(
        self, x1: float, y1: float, x2: float, y2: float
    ):
        """
        属性测试：Player 和 Collectible 的碰撞检测
        """
        player = Player(position=(x1, y1), size=(40, 40))
        collectible = Collectible(position=(x2, y2), size=(24, 24))
        
        # 获取矩形
        player_rect = player.rect
        collectible_rect = collectible.rect
        
        # 检测碰撞
        collision = check_collision(player_rect, collectible_rect)
        
        # 手动验证
        x_overlap = not (player_rect.right <= collectible_rect.left or 
                        player_rect.left >= collectible_rect.right)
        y_overlap = not (player_rect.bottom <= collectible_rect.top or 
                        player_rect.top >= collectible_rect.bottom)
        expected = x_overlap and y_overlap
        
        assert collision == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
