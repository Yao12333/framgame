"""游戏管理器 - 核心游戏逻辑"""
import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from entities.player import Player
from entities.boss import Boss
from effects.damage_system import DamageSystemManager


class GameManager:
    """游戏管理器 - 单例模式"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._players = {}
        self._boss = None
        self._damage_system = DamageSystemManager()
        self._game_running = False
    
    def add_player(self, player_name, player_id, position=(0, 0)):
        player = Player(position, player_name, player_id)
        self._players[player.id] = player
        return player
    
    def remove_player(self, player_id):
        if player_id in self._players:
            del self._players[player_id]
    
    def spawn_boss(self, boss_type="default", position=(500, 300)):
        self._boss = Boss(position, boss_type)
        return self._boss
    
    def get_player(self, player_id):
        return self._players.get(player_id)
    
    def get_all_players(self):
        return list(self._players.values())
    
    def get_nearby_players(self, position, radius):
        nearby = []
        for player in self._players.values():
            if not player._is_alive:
                continue
            dx = player.position['x'] - position['x']
            dy = player.position['y'] - position['y']
            distance = math.sqrt(dx*dx + dy*dy)
            if distance <= radius:
                nearby.append(player)
        return nearby
    
    def update(self, delta_time):
        # 更新所有玩家
        for player in self._players.values():
            player.update(delta_time)
        
        # 更新Boss
        if self._boss and self._boss._is_alive:
            self._boss.update(delta_time)
            # Boss AI - 攻击最近的玩家
            if self._boss.can_use_ability():
                alive_players = [p for p in self._players.values() if p._is_alive]
                if alive_players:
                    result = self._boss.use_ability(alive_players)
                    if result:
                        self._on_boss_attack(result)
        
        # 更新伤害数字
        self._damage_system.update(delta_time)
    
    def _on_boss_attack(self, attack_result):
        # 可以在这里添加伤害数字显示等
        pass
    
    def player_attack_boss(self, player_id, skill_index):
        player = self._players.get(player_id)
        if not player or not player._is_alive:
            return None
        if not self._boss or not self._boss._is_alive:
            return None
        
        damage = player.use_skill(skill_index, self._boss)
        if damage:
            self._damage_system.add_damage(
                damage, self._boss.position, 
                player.player_id, is_critical=(damage > 150)
            )
        return damage
    
    def get_game_state(self):
        return {
            'players': [p.to_dict() for p in self._players.values()],
            'boss': self._boss.to_dict() if self._boss else None,
            'damage_numbers': self._damage_system.get_render_data()
        }
    
    def is_game_over(self):
        if self._boss and not self._boss._is_alive:
            return {'result': 'victory'}
        alive_players = [p for p in self._players.values() if p._is_alive]
        if not alive_players:
            return {'result': 'defeat'}
        return None


# 全局实例
game_manager = GameManager()
