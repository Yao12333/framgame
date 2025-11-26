"""特效管理器 - 单例模式"""


class EffectManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._effects = []
        return cls._instance
    
    def create_projectile(self, effect_type, from_pos, to_pos):
        self._effects.append({
            'type': 'projectile', 'effect_type': effect_type,
            'from': from_pos.copy() if isinstance(from_pos, dict) else {'x': from_pos[0], 'y': from_pos[1]},
            'to': to_pos.copy() if isinstance(to_pos, dict) else {'x': to_pos[0], 'y': to_pos[1]},
            'lifetime': 1.0
        })
    
    def create_explosion(self, effect_type, position, radius):
        pos = position.copy() if isinstance(position, dict) else {'x': position[0], 'y': position[1]}
        self._effects.append({'type': 'explosion', 'effect_type': effect_type, 'position': pos, 'radius': radius, 'lifetime': 0.5})
    
    def create_area_effect(self, effect_type, position, radius):
        pos = position.copy() if isinstance(position, dict) else {'x': position[0], 'y': position[1]}
        self._effects.append({'type': 'area', 'effect_type': effect_type, 'position': pos, 'radius': radius, 'lifetime': 2.0})
    
    def update(self, delta_time):
        for e in self._effects:
            e['lifetime'] -= delta_time
        self._effects = [e for e in self._effects if e['lifetime'] > 0]
    
    def get_effects(self):
        return self._effects.copy()


effect_manager = EffectManager()
