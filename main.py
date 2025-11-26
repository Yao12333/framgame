"""游戏主入口"""
import time
import sys
sys.path.insert(0, '.')

from core.game_manager import game_manager
from entities.skills import Fireball, IceSpear, QuickHeal


def demo_game():
    """演示游戏核心功能"""
    print("=" * 50)
    print("Multiplayer Roguelike - Demo")
    print("=" * 50)
    
    # 创建玩家
    player1 = game_manager.add_player("Warrior", 1, (100, 100))
    player2 = game_manager.add_player("Mage", 2, (150, 100))
    
    # 给玩家添加技能
    player1.add_skill(Fireball())
    player1.add_skill(QuickHeal())
    player2.add_skill(IceSpear())
    player2.add_skill(Fireball())
    
    print(f"\nPlayers created:")
    print(f"  - {player1.name} (HP: {player1._current_health}/{player1._max_health})")
    print(f"  - {player2.name} (HP: {player2._current_health}/{player2._max_health})")
    
    # 生成Boss
    boss = game_manager.spawn_boss("Dragon", (500, 300))
    print(f"\nBoss spawned: {boss.boss_type}")
    print(f"  HP: {boss._current_health}/{boss._max_health}")
    
    # 模拟战斗
    print("\n--- Battle Start ---\n")
    
    round_num = 1
    while True:
        print(f"Round {round_num}:")
        
        # 玩家攻击
        for player in game_manager.get_all_players():
            if player._is_alive:
                damage = game_manager.player_attack_boss(player.id, 0)
                if damage:
                    print(f"  {player.name} deals {damage} damage!")
        
        # 更新游戏状态
        game_manager.update(0.1)
        
        # 检查游戏结束
        result = game_manager.is_game_over()
        if result:
            print(f"\n--- Game Over: {result['result'].upper()} ---")
            break
        
        # 显示Boss状态
        print(f"  Boss HP: {boss._current_health}/{boss._max_health} (Phase {boss._phase})")
        
        round_num += 1
        if round_num > 500:
            print("\n--- Demo ended (max rounds reached) ---")
            break
    
    print("\nFinal game state:")
    state = game_manager.get_game_state()
    print(f"  Players alive: {sum(1 for p in state['players'] if p['is_alive'])}")


if __name__ == "__main__":
    demo_game()
