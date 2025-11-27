"""
移动和碰撞属性测试模块

测试基于 delta_time 的位置更新和碰撞检测
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
import math

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tutorial.entities.player import Player
from tutorial.entities.collectible import Collectible


class TestDeltaTimeMovement:
    """
    **Feature: pygame-tutorial-framework, Property 3: 基于 delta_time 的位置更新**
    
    **Validates: Requirements 5.3**
    
    测试：对于任意 Entity 实例，给定初始位置 (x, y)、速度 (vx, vy) 和时间增量 dt，
    调用 update(dt) 后，新位置应该等于 (x + vx*dt, y + vy*dt)。
    """
    
    @given(
        x=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        vx=st.floats(min_value=-500, max_value=500, allow_nan=False, allow_infinity=False),
        vy=st.floats(min_value=-500, max_value=500, allow_nan=False, allow_infinity=False),
        dt=st.floats(min_value=0.001, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_player_velocity_update(self, x: float, y: float, vx: float, vy: float, dt: float):
        """
        属性测试：Player 的位置更新遵循物理公式
        
        【注意】
        Player 的 update() 方法会根据按键设置速度，
        所以我们需要直接设置速度然后调用 _apply_velocity
        """
        player = Player(position=(x, y))
        player.set_velocity(vx, vy)
        
        # 记录原始位置
        original_x = player.position['x']
        original_y = player.position['y']
        
        # 直接应用速度（绕过键盘输入逻辑）
        player._apply_velocity(dt)
        
        # 计算期望位置
        expected_x = original_x + vx * dt
        expected_y = original_y + vy * dt
        
        # 验证（使用近似比较处理浮点数精度问题）
        assert abs(player.position['x'] - expected_x) < 1e-6, \
            f"X 位置不正确: 期望 {expected_x}, 实际 {player.position['x']}"
        assert abs(player.position['y'] - expected_y) < 1e-6, \
            f"Y 位置不正确: 期望 {expected_y}, 实际 {player.position['y']}"
    
    @given(
        x=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        dt=st.floats(min_value=0.001, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_collectible_position_oscillates(self, x: float, y: float, dt: float):
        """
        属性测试：Collectible 的浮动动画在合理范围内
        
        Collectible 有浮动动画，位置会在 base_y ± 5 像素范围内变化
        """
        collectible = Collectible(position=(x, y))
        base_y = collectible._base_y
        
        # 更新多次
        for _ in range(10):
            collectible.update(dt)
        
        # 验证 Y 坐标在合理范围内（base_y ± 5 像素）
        current_y = collectible.position['y']
        assert abs(current_y - base_y) <= 5.1, \
            f"Y 坐标超出浮动范围: base={base_y}, current={current_y}"
    
    @given(
        x=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        vx=st.floats(min_value=-500, max_value=500, allow_nan=False, allow_infinity=False),
        vy=st.floats(min_value=-500, max_value=500, allow_nan=False, allow_infinity=False),
        dt1=st.floats(min_value=0.001, max_value=0.5, allow_nan=False, allow_infinity=False),
        dt2=st.floats(min_value=0.001, max_value=0.5, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_movement_is_additive(self, x: float, y: float, vx: float, vy: float, dt1: float, dt2: float):
        """
        属性测试：连续两次移动等于一次移动总时间
        
        move(dt1) + move(dt2) 应该等于 move(dt1 + dt2)
        """
        # 创建两个相同的 Player
        player1 = Player(position=(x, y))
        player1.set_velocity(vx, vy)
        
        player2 = Player(position=(x, y))
        player2.set_velocity(vx, vy)
        
        # player1: 两次移动
        player1._apply_velocity(dt1)
        player1._apply_velocity(dt2)
        
        # player2: 一次移动总时间
        player2._apply_velocity(dt1 + dt2)
        
        # 验证结果相同（考虑浮点数精度）
        assert abs(player1.position['x'] - player2.position['x']) < 1e-5, \
            "X 位置不一致"
        assert abs(player1.position['y'] - player2.position['y']) < 1e-5, \
            "Y 位置不一致"


class TestPlayerCollectibleRoundTrip:
    """
    Player 和 Collectible 的序列化 round-trip 测试
    
    扩展 Property 2 测试到具体子类
    """
    
    @given(
        x=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        score=st.integers(min_value=0, max_value=10000),
        speed=st.floats(min_value=50, max_value=500, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_player_round_trip(self, x: float, y: float, score: int, speed: float):
        """Player 序列化 round-trip"""
        original = Player(position=(x, y), speed=speed)
        original._score = score
        
        data = original.to_dict()
        restored = Player.from_dict(data)
        
        assert abs(restored.position['x'] - original.position['x']) < 1e-6
        assert abs(restored.position['y'] - original.position['y']) < 1e-6
        assert restored.score == original.score
        assert abs(restored.speed - original.speed) < 1e-6
    
    @given(
        x=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        points=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=100)
    def test_collectible_round_trip(self, x: float, y: float, points: int):
        """Collectible 序列化 round-trip"""
        original = Collectible(position=(x, y), points=points)
        
        data = original.to_dict()
        restored = Collectible.from_dict(data)
        
        assert abs(restored.position['x'] - original.position['x']) < 1e-6
        assert abs(restored.position['y'] - original.position['y']) < 1e-6
        assert restored.points == original.points


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
