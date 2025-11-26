"""玩家类 - 继承练习"""
from .base_entity import LivingEntity


class Player(LivingEntity):
    """玩家类"""
    
    def __init__(self, position, player_name, player_id):
        super().__init__(position, health=200)
        self.name = player_name
        self.player_id = player_id
        self._level = 1
        self._experience = 0
        self._skills = []
        self._equipment = {}
        self._respawn_timer = 0
    
    def update(self, delta_time):
        if not self._is_alive:
            self._respawn_timer -= delta_time
            return
        self.move(delta_time)
        self.update_status_effects(delta_time)
        self._update_skills(delta_time)
    
    def _update_skills(self, delta_time):
        for skill in self._skills:
            skill.update_cooldown(delta_time)
    
    def on_death(self, killer_id):
        print(f"Player {self.name} was defeated!")
        self._respawn_timer = 10.0
    
    def gain_experience(self, amount):
        self._experience += amount
        while self._experience >= self._get_level_requirement():
            self._level_up()
    
    def _level_up(self):
        self._experience -= self._get_level_requirement()
        self._level += 1
        self._max_health += 20
        self._current_health = self._max_health
        print(f"{self.name} reached level {self._level}!")
    
    def _get_level_requirement(self):
        return self._level * 100
    
    def add_skill(self, skill):
        self._skills.append(skill)
    
    def use_skill(self, skill_index, target=None):
        if 0 <= skill_index < len(self._skills):
            return self._skills[skill_index].execute(self, target)
        return False
    
    def to_dict(self):
        return {
            'id': self._id,
            'name': self.name,
            'player_id': self.player_id,
            'position': self._position,
            'health': self._current_health,
            'max_health': self._max_health,
            'level': self._level,
            'is_alive': self._is_alive
        }
