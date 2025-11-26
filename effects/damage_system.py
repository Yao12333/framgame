"""伤害数字系统 - 封装练习"""
import random


class DamageNumber:
    """单个伤害数字的封装"""
    
    def __init__(self, value, position, player_id, is_critical=False):
        self._value = value
        self._position = position.copy()
        self._player_id = player_id
        self._is_critical = is_critical
        self._lifetime = 2.0
        self._velocity = {'x': random.uniform(-30, 30), 'y': -120 if is_critical else -80}
        self._color = {1: '#FF6B6B', 2: '#4ECDC4', 3: '#45B7D1', 4: '#96CEB4'}.get(player_id, '#FFFFFF')
    
    def update(self, delta_time):
        self._position['x'] += self._velocity['x'] * delta_time
        self._position['y'] += self._velocity['y'] * delta_time
        self._velocity['y'] += 200 * delta_time
        self._lifetime -= delta_time
        return self._lifetime > 0
    
    @property
    def is_alive(self):
        return self._lifetime > 0
    
    @property
    def render_data(self):
        return {
            'text': self._format_damage(),
            'x': self._position['x'],
            'y': self._position['y'],
            'color': self._color,
            'size': 48 if self._is_critical else 32,
            'alpha': max(0, self._lifetime / 2.0)
        }
    
    def _format_damage(self):
        if self._value >= 1000000:
            return f"{self._value/1000000:.1f}M"
        elif self._value >= 1000:
            return f"{self._value/1000:.1f}K"
        return str(self._value)


class DamageSystemManager:
    """伤害系统管理器"""
    
    def __init__(self, max_numbers=100):
        self._damage_numbers = []
        self._max_numbers = max_numbers
    
    def add_damage(self, value, position, player_id, is_critical=False):
        self._damage_numbers.append(DamageNumber(value, position, player_id, is_critical))
        if len(self._damage_numbers) > self._max_numbers:
            self._damage_numbers.pop(0)
    
    def update(self, delta_time):
        self._damage_numbers = [d for d in self._damage_numbers if d.update(delta_time)]
    
    def get_render_data(self):
        return [d.render_data for d in self._damage_numbers]
