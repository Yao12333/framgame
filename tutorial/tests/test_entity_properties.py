"""
Entity 属性测试模块

使用 hypothesis 库进行属性测试 (Property-Based Testing)

【属性测试 vs 单元测试】
- 单元测试：测试特定的输入和预期输出
- 属性测试：测试对于所有可能输入都应该成立的"属性"

【hypothesis 库】
hypothesis 会自动生成大量随机测试数据，帮助发现边界情况的 bug
"""

import pytest
from hypothesis import given, strategies as st, settings

# 导入要测试的类
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tutorial.entities.base import Entity
from typing import Dict, Any


# 创建一个具体的 Entity 子类用于测试（因为 Entity 是抽象类）
class ConcreteEntity(Entity):
    """用于测试的具体实体类"""
    
    def update(self, delta_time: float) -> None:
        """实现抽象方法：应用速度更新位置"""
        self._apply_velocity(delta_time)
    
    def render(self, screen) -> None:
        """实现抽象方法：渲染（测试中不需要实际渲染）"""
        pass
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConcreteEntity':
        """从字典创建实体"""
        position = (data['position']['x'], data['position']['y'])
        size = tuple(data['size'])
        color = tuple(data['color'])
        
        entity = cls(position=position, size=size, color=color)
        
        # 恢复其他属性
        if 'id' in data:
            entity._id = data['id']
        if 'velocity' in data:
            entity._velocity = data['velocity'].copy()
        if 'is_active' in data:
            entity._is_active = data['is_active']
        
        return entity


# ==================== Property 1 测试 ====================

class TestPositionPropertyCopy:
    """
    **Feature: pygame-tutorial-framework, Property 1: Position property 返回副本保护封装**
    
    **Validates: Requirements 2.1, 2.2**
    
    测试 position property 返回的是副本而非原始引用，
    修改返回值不应影响实体的内部状态。
    """
    
    @given(
        x=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        new_x=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        new_y=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_position_returns_copy(self, x: float, y: float, new_x: float, new_y: float):
        """
        属性测试：修改 position 返回值不影响内部状态
        
        【测试逻辑】
        1. 创建实体，设置初始位置 (x, y)
        2. 获取 position 属性
        3. 修改获取到的字典
        4. 验证实体内部位置没有改变
        """
        # 创建实体
        entity = ConcreteEntity(position=(x, y))
        
        # 记录原始位置
        original_x = entity.position['x']
        original_y = entity.position['y']
        
        # 获取 position 并修改
        pos = entity.position
        pos['x'] = new_x
        pos['y'] = new_y
        
        # 验证内部状态没有改变
        assert entity.position['x'] == original_x, \
            f"内部 x 坐标被意外修改: 期望 {original_x}, 实际 {entity.position['x']}"
        assert entity.position['y'] == original_y, \
            f"内部 y 坐标被意外修改: 期望 {original_y}, 实际 {entity.position['y']}"
    
    @given(
        x=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_multiple_position_calls_return_independent_copies(self, x: float, y: float):
        """
        属性测试：多次调用 position 返回独立的副本
        
        【测试逻辑】
        1. 创建实体
        2. 多次获取 position
        3. 验证每次返回的是不同的对象
        """
        entity = ConcreteEntity(position=(x, y))
        
        pos1 = entity.position
        pos2 = entity.position
        
        # 验证是不同的对象（不同的内存地址）
        assert pos1 is not pos2, "多次调用 position 应该返回不同的对象"
        
        # 验证内容相同
        assert pos1 == pos2, "多次调用 position 返回的内容应该相同"


# ==================== Property 2 测试 ====================

class TestEntitySerializationRoundTrip:
    """
    **Feature: pygame-tutorial-framework, Property 2: Entity 序列化 round-trip**
    
    **Validates: Requirements 3.4, 3.5**
    
    测试 to_dict() 然后 from_dict() 应该产生等价的对象。
    """
    
    @given(
        x=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        vx=st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        vy=st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
        width=st.integers(min_value=1, max_value=200),
        height=st.integers(min_value=1, max_value=200),
        r=st.integers(min_value=0, max_value=255),
        g=st.integers(min_value=0, max_value=255),
        b=st.integers(min_value=0, max_value=255),
        is_active=st.booleans()
    )
    @settings(max_examples=100)
    def test_serialization_round_trip(
        self, x: float, y: float, vx: float, vy: float,
        width: int, height: int, r: int, g: int, b: int, is_active: bool
    ):
        """
        属性测试：序列化后反序列化应该得到等价的对象
        
        【测试逻辑】
        1. 创建实体，设置各种属性
        2. 调用 to_dict() 序列化
        3. 调用 from_dict() 反序列化
        4. 验证新对象的所有属性与原对象相同
        """
        # 创建原始实体
        original = ConcreteEntity(
            position=(x, y),
            size=(width, height),
            color=(r, g, b)
        )
        original.set_velocity(vx, vy)
        if not is_active:
            original.deactivate()
        
        # 序列化
        data = original.to_dict()
        
        # 反序列化
        restored = ConcreteEntity.from_dict(data)
        
        # 验证所有属性相同
        assert restored.position['x'] == original.position['x'], "x 坐标不匹配"
        assert restored.position['y'] == original.position['y'], "y 坐标不匹配"
        assert restored.velocity['x'] == original.velocity['x'], "vx 不匹配"
        assert restored.velocity['y'] == original.velocity['y'], "vy 不匹配"
        assert restored.size == original.size, "尺寸不匹配"
        assert restored.color == original.color, "颜色不匹配"
        assert restored.is_active == original.is_active, "激活状态不匹配"
        assert restored.id == original.id, "ID 不匹配"
    
    @given(
        x=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        y=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_to_dict_contains_required_fields(self, x: float, y: float):
        """
        属性测试：to_dict() 返回的字典包含所有必要字段
        """
        entity = ConcreteEntity(position=(x, y))
        data = entity.to_dict()
        
        required_fields = ['type', 'id', 'position', 'velocity', 'size', 'color', 'is_active']
        for field in required_fields:
            assert field in data, f"to_dict() 缺少字段: {field}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
