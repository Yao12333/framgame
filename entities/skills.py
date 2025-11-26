"""技能系统 - 继承练习"""
from abc import ABC, abstractmethod
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from effects.effect_manager import effect_manager


class Skill(ABC):
    """技能基类"""
    
    def __init__(self, name, cooldown, damage=0):
        self.name = name
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.base_damage = damage
    
    @abstractmethod
    def execute(self, caster, target=None):
        pass
    
    def can_use(self):
        return self.current_cooldown <= 0
    
    def update_cooldown(self, delta_time):
        if self.current_cooldown > 0:
            self.current_cooldown -= delta_time


class DamageSkill(Skill):
    """伤害技能基类"""
    
    def __init__(self, name, cooldown, damage, damage_type="physical"):
        super().__init__(name, cooldown, damage)
        self.damage_type = damage_type
    
    def execute(self, caster, target):
        if not self.can_use() or target is None:
            return False
        damage = self._calculate_damage(caster)
        actual_damage = target.take_damage(damage, caster.id)
        self.current_cooldown = self.cooldown
        self._create_visual_effect(caster.position, target.position)
        return actual_damage
    
    def _calculate_damage(self, caster):
        return self.base_damage
    
    @abstractmethod
    def _create_visual_effect(self, from_pos, to_pos):
        pass


class Fireball(DamageSkill):
    """火球术"""
    
    def __init__(self):
        super().__init__("Fireball", cooldown=2.0, damage=150, damage_type="fire")
        self.explosion_radius = 50
    
    def _calculate_damage(self, caster):
        import random
        return int(self.base_damage * random.uniform(0.8, 1.2))
    
    def _create_visual_effect(self, from_pos, to_pos):
        effect_manager.create_projectile("fireball", from_pos, to_pos)
        effect_manager.create_explosion("fire", to_pos, self.explosion_radius)


class IceSpear(DamageSkill):
    """冰矛"""
    
    def __init__(self):
        super().__init__("Ice Spear", cooldown=3.0, damage=200, damage_type="ice")
    
    def _create_visual_effect(self, from_pos, to_pos):
        effect_manager.create_projectile("ice_spear", from_pos, to_pos)


class HealingSkill(Skill):
    """治疗技能基类"""
    
    def __init__(self, name, cooldown, heal_amount):
        super().__init__(name, cooldown)
        self.heal_amount = heal_amount
    
    def execute(self, caster, target=None):
        if not self.can_use():
            return False
        target = target or caster
        target.heal(self.heal_amount)
        self.current_cooldown = self.cooldown
        self._create_heal_effect(target.position)
        return self.heal_amount
    
    @abstractmethod
    def _create_heal_effect(self, position):
        pass


class QuickHeal(HealingSkill):
    """快速治疗"""
    
    def __init__(self):
        super().__init__("Quick Heal", cooldown=5.0, heal_amount=80)
    
    def _create_heal_effect(self, position):
        effect_manager.create_area_effect("heal_single", position, 20)


class GroupHeal(HealingSkill):
    """群体治疗"""
    
    def __init__(self):
        super().__init__("Group Heal", cooldown=10.0, heal_amount=100)
        self.heal_radius = 100
    
    def _create_heal_effect(self, position):
        effect_manager.create_area_effect("healing_circle", position, self.heal_radius)
