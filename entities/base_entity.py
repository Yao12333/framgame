"""实体基类 - 继承练习"""
from abc import ABC, abstractmethod
import uuid


class Entity(ABC):
    """所有游戏实体的基类"""
    
    def __init__(self, position, health=100):
        self._id = str(uuid.uuid4())
        self._position = {'x': position[0], 'y': position[1]}
        self._max_health = health
        self._current_health = health
        self._is_alive = True
        self._velocity = {'x': 0, 'y': 0}
    
    @property
    def id(self):
        return self._id
    
    @property
    def position(self):
        return self._position.copy()
    
    @property
    def health_percentage(self):
        return self._current_health / self._max_health
    
    @abstractmethod
    def update(self, delta_time):
        pass
    
    @abstractmethod
    def take_damage(self, damage, attacker_id=None):
        pass
    
    def move(self, delta_time):
        self._position['x'] += self._velocity['x'] * delta_time
        self._position['y'] += self._velocity['y'] * delta_time
    
    def heal(self, amount):
        self._current_health = min(self._max_health, self._current_health + amount)


class LivingEntity(Entity):
    """活体实体基类"""
    
    def __init__(self, position, health=100):
        super().__init__(position, health)
        self._status_effects = []
        self._defense = 0
    
    def take_damage(self, damage, attacker_id=None):
        actual_damage = max(1, damage - self._defense)
        self._current_health -= actual_damage
        if self._current_health <= 0:
            self._current_health = 0
            self._is_alive = False
            self.on_death(attacker_id)
        return actual_damage
    
    def add_status_effect(self, effect):
        self._status_effects.append(effect)
    
    def update_status_effects(self, delta_time):
        active = []
        for effect in self._status_effects:
            effect.update(delta_time)
            if effect.is_active:
                active.append(effect)
            else:
                effect.on_remove(self)
        self._status_effects = active
    
    @abstractmethod
    def on_death(self, killer_id):
        pass
