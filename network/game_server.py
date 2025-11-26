"""游戏服务器 - 多线程练习"""
import threading
import socket
import json
import queue
import time
from concurrent.futures import ThreadPoolExecutor


class ClientConnection:
    """客户端连接封装"""
    
    def __init__(self, client_id, sock, address, server):
        self.client_id = client_id
        self.socket = sock
        self.address = address
        self.server = server
        self.connected = True
        self.send_lock = threading.Lock()
    
    def receive_message(self):
        try:
            length_data = self.socket.recv(4)
            if not length_data:
                return None
            msg_len = int.from_bytes(length_data, byteorder='big')
            message = b''
            while len(message) < msg_len:
                chunk = self.socket.recv(msg_len - len(message))
                if not chunk:
                    return None
                message += chunk
            return message.decode('utf-8')
        except Exception as e:
            print(f"Receive error from {self.client_id}: {e}")
            return None
    
    def send_message(self, message):
        with self.send_lock:
            try:
                data = message.encode('utf-8')
                length = len(data).to_bytes(4, byteorder='big')
                self.socket.send(length + data)
                return True
            except Exception as e:
                print(f"Send error to {self.client_id}: {e}")
                self.connected = False
                return False


class GameServer:
    """多线程游戏服务器"""
    
    def __init__(self, host='localhost', port=8080, max_players=4):
        self.host = host
        self.port = port
        self.max_players = max_players
        self.clients = {}
        self.game_state = {'players': [], 'boss': None, 'effects': []}
        self.message_queue = queue.Queue()
        self.clients_lock = threading.RLock()
        self.game_state_lock = threading.RLock()
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        self.running = False
        self.server_socket = None
    
    def start(self):
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_players)
        print(f"Server started on {self.host}:{self.port}")
        
        threading.Thread(target=self._accept_connections, daemon=True).start()
        threading.Thread(target=self._game_loop, daemon=True).start()
        threading.Thread(target=self._message_processor, daemon=True).start()
    
    def _accept_connections(self):
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                with self.clients_lock:
                    if len(self.clients) >= self.max_players:
                        client_socket.send(b"Server full")
                        client_socket.close()
                        continue
                    client_id = f"player_{len(self.clients) + 1}"
                    client_conn = ClientConnection(client_id, client_socket, address, self)
                    self.clients[client_id] = client_conn
  

                self.thread_pool.submit(self._handle_client, client_conn)
                print(f"Player {client_id} connected from {address}")
            except Exception as e:
                if self.running:
                    print(f"Accept error: {e}")
    
    def _handle_client(self, client_conn):
        try:
            while self.running and client_conn.connected:
                data = client_conn.receive_message()
                if data:
                    self.message_queue.put((client_conn.client_id, data))
                else:
                    break
        except Exception as e:
            print(f"Handle client error {client_conn.client_id}: {e}")
        finally:
            self._disconnect_client(client_conn.client_id)
    
    def _message_processor(self):
        while self.running:
            try:
                client_id, message = self.message_queue.get(timeout=1.0)
                self._process_game_message(client_id, message)
                self.message_queue.task_done()
            except queue.Empty:
                continue
    
    def _game_loop(self):
        target_fps = 60
        frame_time = 1.0 / target_fps
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time
            
            with self.game_state_lock:
                self._update_game_state(delta_time)
            self._broadcast_game_state()
            
            elapsed = time.time() - current_time
            time.sleep(max(0, frame_time - elapsed))
    
    def _update_game_state(self, delta_time):
        for player in self.game_state.get('players', []):
            player.update(delta_time)
        boss = self.game_state.get('boss')
        if boss:
            boss.update(delta_time)
    
    def _broadcast_game_state(self):
        state_data = json.dumps(self._serialize_game_state())
        with self.clients_lock:
            disconnected = []
            for client_id, conn in self.clients.items():
                if not conn.send_message(state_data):
                    disconnected.append(client_id)
            for cid in disconnected:
                self._disconnect_client(cid)
    
    def _serialize_game_state(self):
        return {
            'players': [p.to_dict() for p in self.game_state.get('players', [])],
            'boss': self.game_state['boss'].to_dict() if self.game_state.get('boss') else None
        }
    
    def _process_game_message(self, client_id, message):
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            if msg_type == 'player_action':
                self._handle_player_action(client_id, data)
            elif msg_type == 'skill_use':
                self._handle_skill_use(client_id, data)
        except json.JSONDecodeError:
            print(f"Invalid JSON from {client_id}")
    
    def _handle_player_action(self, client_id, data):
        pass  # 实现玩家行动处理
    
    def _handle_skill_use(self, client_id, data):
        pass  # 实现技能使用处理
    
    def _disconnect_client(self, client_id):
        with self.clients_lock:
            if client_id in self.clients:
                self.clients[client_id].socket.close()
                del self.clients[client_id]
                print(f"Player {client_id} disconnected")
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self.thread_pool.shutdown(wait=False)
