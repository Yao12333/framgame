"""Boss类 - 继承练习"""
from .base_entity import LivingEntity


class Boss(LivingEntity):
    """Boss类"""
    
    def __init__(self, position, boss_type="default"):
        super().__init__(position, health=50000)
        self.boss_type = boss_type
        self._phase = 1
        self._abilities = []
        self._last_ability_time = 0
        self._ability_cooldown = 3.0
    
    def update(self, delta_time):
        if not self._is_alive:
            return
        self.move(delta_time)
        self.update_status_effects(delta_time)
        self._check_phase_change()
        self._last_ability_time += delta_time
    
    def _check_phase_change(self):
        hp = self.health_percentage
        if hp < 0.5 and self._phase == 1:
            self._phase = 2
            self._enter_phase_2()
        elif hp < 0.2 and self._phase == 2:
            self._phase = 3
            self._enter_berserk_mode()
    
    def _enter_phase_2(self):
        print("Boss enters Phase 2!")
        self._ability_cooldown = 2.0
    
    def _enter_berserk_mode(self):
        print("Boss enters BERSERK MODE!")
        self._defense += 50
        self._ability_cooldown = 1.0
    
    def on_death(self, killer_id):
        print("Boss defeated! Victory!")
        self._drop_loot()
    
    def _drop_loot(self):
        # 根据Boss类型掉落不同物品
        loot = {'gold': 1000, 'items': ['epic_sword', 'rare_armor']}
        return loot
    
    def can_use_ability(self):
        return self._last_ability_time >= self._ability_cooldown
    
    def use_ability(self, targets):
        if not self.can_use_ability():
            return None
        self._last_ability_time = 0
        # 根据阶段使用不同技能
        if self._phase == 1:
            return self._basic_attack(targets)
        elif self._phase == 2:
            return self._aoe_attack(targets)
        else:
            return self._berserk_attack(targets)
    
    def _basic_attack(self, targets):
        if targets:
            damage = 50
            targets[0].take_damage(damage, self._id)
            return {'type': 'basic', 'damage': damage, 'target': targets[0]._id}
        return None
    
    def _aoe_attack(self, targets):
        damage = 30
        for t in targets:
            t.take_damage(damage, self._id)
        return {'type': 'aoe', 'damage': damage, 'targets': [t._id for t in targets]}
    
    def _berserk_attack(self, targets):
        if targets:
            damage = 100
            targets[0].take_damage(damage, self._id)
            return {'type': 'berserk', 'damage': damage, 'target': targets[0]._id}
        return None
    
    def to_dict(self):
        return {
            'id': self._id,
            'boss_type': self.boss_type,
            'position': self._position,
            'health': self._current_health,
            'max_health': self._max_health,
            'phase': self._phase,
            'is_alive': self._is_alive
        }
