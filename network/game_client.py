"""游戏客户端 - 多线程练习"""
import threading
import socket
import json
import queue


class GameClient:
    """游戏客户端网络管理"""
    
    def __init__(self):
        self.socket = None
        self.connected = False
        self.incoming_messages = queue.Queue()
        self.outgoing_messages = queue.Queue()
        self.receive_thread = None
        self.send_thread = None
    
    def connect(self, host, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.send_thread = threading.Thread(target=self._send_loop, daemon=True)
            self.receive_thread.start()
            self.send_thread.start()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def _receive_loop(self):
        while self.connected:
            try:
                length_data = self.socket.recv(4)
                if not length_data:
                    break
                msg_len = int.from_bytes(length_data, byteorder='big')
                message = b''
                while len(message) < msg_len:
                    chunk = self.socket.recv(msg_len - len(message))
                    if not chunk:
                        break
                    message += chunk
                if len(message) == msg_len:
                    self.incoming_messages.put(message.decode('utf-8'))
            except Exception as e:
                print(f"Receive error: {e}")
                break
        self.connected = False
    
    def _send_loop(self):
        while self.connected:
            try:
                message = self.outgoing_messages.get(timeout=1.0)
                data = message.encode('utf-8')
                length = len(data).to_bytes(4, byteorder='big')
                self.socket.send(length + data)
                self.outgoing_messages.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Send error: {e}")
                break
    
    def send_player_action(self, action, data):
        message = json.dumps({'type': 'player_action', 'action': action, 'data': data})
        self.outgoing_messages.put(message)
    
    def send_skill_use(self, skill_index, target_id=None):
        message = json.dumps({'type': 'skill_use', 'skill_index': skill_index, 'target_id': target_id})
        self.outgoing_messages.put(message)
    
    def get_messages(self):
        messages = []
        while not self.incoming_messages.empty():
            try:
                messages.append(json.loads(self.incoming_messages.get_nowait()))
            except queue.Empty:
                break
        return messages
    
    def disconnect(self):
        self.connected = False
        if self.socket:
            self.socket.close()
