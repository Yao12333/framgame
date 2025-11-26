"""游戏配置系统 - 封装练习"""
import json


class GameConfig:
    def __init__(self, config_path='config.json'):
        self._config_path = config_path
        self._config = {
            'graphics': {'screen_width': 1920, 'screen_height': 1080, 'fps': 60, 'vsync': True},
            'gameplay': {'max_players': 4, 'damage_multiplier': 1.0, 'boss_health_scale': 1.5},
            'network': {'server_host': 'localhost', 'server_port': 8080, 'timeout': 30}
        }
        self._load_from_file()
    
    def _load_from_file(self):
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                self._merge_config(json.load(f))
        except FileNotFoundError:
            self._save_to_file()
    
    def _save_to_file(self):
        with open(self._config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2)
    
    def _merge_config(self, user_config):
        def merge(base, override):
            for k, v in override.items():
                if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                    merge(base[k], v)
                else:
                    base[k] = v
        merge(self._config, user_config)
    
    @property
    def screen_resolution(self):
        return (self._config['graphics']['screen_width'], self._config['graphics']['screen_height'])
    
    @property
    def max_players(self):
        return self._config['gameplay']['max_players']
    
    @property
    def fps(self):
        return self._config['graphics']['fps']
    
    def get_network_config(self):
        return self._config['network'].copy()
    
    def update_setting(self, category, key, value):
        if category in self._config and key in self._config[category]:
            self._config[category][key] = value
            self._save_to_file()
            return True
        return False
