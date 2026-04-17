#!/usr/bin/env python3
"""
P2P Core - Shared backend for TUI and GUI
Ultra-minimalist, feature-rich P2P file transfer
"""

import socket
import threading
import hashlib
import json
import time
import platform
import uuid
import gzip
from pathlib import Path
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.fernet import Fernet
import base64


def get_local_ip() -> str:
    """Get local IP address automatically"""
    try:
        # Create a socket to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


class MessageType(Enum):
    HANDSHAKE_INIT = "handshake_init"
    HANDSHAKE_RESPONSE = "handshake_response"
    AUTH_REQUEST = "auth_request"
    AUTH_RESPONSE = "auth_response"
    FILE_LIST_REQUEST = "file_list_request"
    FILE_LIST_RESPONSE = "file_list_response"
    FILE_TRANSFER_INIT = "file_transfer_init"
    FILE_CHUNK = "file_chunk"
    FILE_COMPLETE = "file_complete"
    TRANSFER_PAUSE = "transfer_pause"
    TRANSFER_RESUME = "transfer_resume"
    TRANSFER_CANCEL = "transfer_cancel"
    PING = "ping"
    PONG = "pong"
    DISCONNECT = "disconnect"


@dataclass
class FileMetadata:
    name: str
    size: int
    hash: str
    path: str
    modified: float = 0.0


@dataclass
class TransferStats:
    filename: str
    total_size: int
    transferred: int
    speed: float
    eta: float
    status: str  # 'active', 'paused', 'complete', 'failed'
    start_time: float


@dataclass
class PeerInfo:
    device_id: str
    ip: str
    nickname: str = ""
    last_seen: float = 0.0
    status: str = "offline"  # 'online', 'offline', 'connecting'


class DeviceID:
    @staticmethod
    def generate() -> str:
        """Generate unique Device ID for this machine"""
        machine_id = platform.node()
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                                for elements in range(0, 2*6, 2)][::-1])
        system_info = f"{platform.system()}{platform.machine()}{machine_id}{mac_address}"
        hash_obj = hashlib.sha256(system_info.encode())
        device_id = hash_obj.hexdigest()[:12].upper()
        return '-'.join([device_id[i:i+4] for i in range(0, 12, 4)])
    
    @staticmethod
    def generate_with_ip(port: int = 5000) -> str:
        """Generate Device ID with local IP automatically encoded"""
        ip = get_local_ip()
        return DeviceID.encode_with_ip(ip, port)
    
    @staticmethod
    def encode_with_ip(ip: str, port: int = 5000) -> str:
        """Encode IP:PORT into Device ID format - IP is hidden but recoverable"""
        data = f"{ip}:{port}"
        # Base64 encode but make it look like a device ID
        encoded = base64.b64encode(data.encode()).decode().replace('=', '').replace('+', 'X').replace('/', 'Y')
        # Pad to 12 chars
        encoded = (encoded + '0' * 12)[:12].upper()
        return f"{encoded[:4]}-{encoded[4:8]}-{encoded[8:12]}"
    
    @staticmethod
    def decode_to_ip(device_id: str) -> Optional[tuple]:
        """Decode Device ID back to (IP, PORT)"""
        try:
            # Remove dashes
            encoded = device_id.replace('-', '')
            # Reverse the encoding
            encoded = encoded.replace('X', '+').replace('Y', '/')
            # Add padding
            padding = (4 - len(encoded) % 4) % 4
            encoded += '=' * padding
            # Decode
            decoded = base64.b64decode(encoded).decode()
            if ':' in decoded:
                ip, port = decoded.split(':')
                return (ip, int(port))
        except:
            pass
        return None
    
    @staticmethod
    def save(device_id: str, filepath: Path):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(device_id)
    
    @staticmethod
    def load(filepath: Path) -> Optional[str]:
        return filepath.read_text().strip() if filepath.exists() else None


class PeerRegistry:
    def __init__(self, registry_file: Path):
        self.registry_file = registry_file
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.peers: Dict[str, PeerInfo] = {}
        self.load()
    
    def load(self):
        if self.registry_file.exists():
            try:
                data = json.loads(self.registry_file.read_text())
                self.peers = {k: PeerInfo(**v) for k, v in data.items()}
            except:
                self.peers = {}
    
    def save(self):
        data = {k: asdict(v) for k, v in self.peers.items()}
        self.registry_file.write_text(json.dumps(data, indent=2))
    
    def add_peer(self, device_id: str, ip: str, nickname: str = ""):
        """Add peer with Device ID that contains IP info"""
        self.peers[device_id] = PeerInfo(device_id, ip, nickname, time.time(), "offline")
        self.save()
    
    def add_peer_by_device_id(self, device_id_with_ip: str, nickname: str = "") -> bool:
        """Add peer using only Device ID (which contains encoded IP)"""
        # For now, we still need IP separately stored
        # User will input Device ID, we extract IP from our registry
        return False
    
    def get_ip_from_device_id(self, device_id: str) -> Optional[str]:
        """Get IP address from Device ID"""
        peer = self.peers.get(device_id)
        return peer.ip if peer else None
    
    def get_peer(self, device_id: str) -> Optional[PeerInfo]:
        return self.peers.get(device_id)
    
    def get_all_peers(self) -> List[PeerInfo]:
        return list(self.peers.values())
    
    def remove_peer(self, device_id: str):
        if device_id in self.peers:
            del self.peers[device_id]
            self.save()
    
    def update_status(self, device_id: str, status: str):
        if device_id in self.peers:
            self.peers[device_id].status = status
            self.peers[device_id].last_seen = time.time()
            self.save()


class CryptoManager:
    def __init__(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()
        self.symmetric_key: Optional[bytes] = None
        self.cipher: Optional[Fernet] = None
    
    def get_public_key_bytes(self) -> bytes:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def decrypt_symmetric_key(self, encrypted_key: bytes) -> bytes:
        return self.private_key.decrypt(
            encrypted_key,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(), label=None)
        )
    
    def encrypt_symmetric_key(self, public_key_bytes: bytes, symmetric_key: bytes) -> bytes:
        public_key = serialization.load_pem_public_key(public_key_bytes)
        return public_key.encrypt(
            symmetric_key,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(), label=None)
        )
    
    def generate_symmetric_key(self) -> bytes:
        return Fernet.generate_key()
    
    def set_symmetric_key(self, key: bytes):
        self.symmetric_key = key
        self.cipher = Fernet(key)
    
    def encrypt(self, data: bytes) -> bytes:
        if not self.cipher:
            raise ValueError("Symmetric key not set")
        return self.cipher.encrypt(data)
    
    def decrypt(self, data: bytes) -> bytes:
        if not self.cipher:
            raise ValueError("Symmetric key not set")
        return self.cipher.decrypt(data)
    
    def get_key_fingerprint(self) -> str:
        key_bytes = self.get_public_key_bytes()
        return hashlib.sha256(key_bytes).hexdigest()[:16].upper()


class FileManager:
    def __init__(self, shared_dir: Path):
        self.shared_dir = shared_dir
        self.shared_dir.mkdir(parents=True, exist_ok=True)
        self.shared_files: List[FileMetadata] = []
    
    def scan_shared_files(self):
        self.shared_files = []
        for file_path in self.shared_dir.rglob('*'):
            if file_path.is_file():
                file_hash = self.calculate_hash(file_path)
                relative_path = file_path.relative_to(self.shared_dir)
                metadata = FileMetadata(
                    name=str(relative_path),
                    size=file_path.stat().st_size,
                    hash=file_hash,
                    path=str(file_path),
                    modified=file_path.stat().st_mtime
                )
                self.shared_files.append(metadata)
    
    @staticmethod
    def calculate_hash(file_path: Path) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def get_file_list(self) -> List[Dict]:
        return [asdict(f) for f in self.shared_files]
    
    def get_file_by_name(self, name: str) -> Optional[FileMetadata]:
        for file in self.shared_files:
            if file.name == name:
                return file
        return None
    
    def add_file_to_shared(self, source_path: Path) -> bool:
        try:
            if not source_path.exists():
                print(f"File not found: {source_path}")
                return False
            if not source_path.is_file():
                print(f"Not a file: {source_path}")
                return False
            
            dest_path = self.shared_dir / source_path.name
            if source_path != dest_path:
                import shutil
                shutil.copy2(source_path, dest_path)
                print(f"Copied: {source_path} -> {dest_path}")
            else:
                print(f"File already in shared folder: {source_path}")
            
            self.scan_shared_files()
            print(f"Scanned, total files: {len(self.shared_files)}")
            return True
        except Exception as e:
            print(f"Error adding file: {e}")
            import traceback
            traceback.print_exc()
            return False


class P2PConnection:
    CHUNK_SIZE = 131072  # 128KB chunks
    
    def __init__(self, sock: socket.socket, device_id: str, crypto: CryptoManager,
                 file_manager: FileManager, is_initiator: bool = False):
        self.sock = sock
        self.device_id = device_id
        self.crypto = crypto
        self.file_manager = file_manager
        self.is_initiator = is_initiator
        self.peer_device_id: Optional[str] = None
        self.authenticated = False
        self.running = False
        self.transfer_stats: Dict[str, TransferStats] = {}
        self.on_auth_request: Optional[Callable] = None
        self.on_transfer_progress: Optional[Callable] = None
        self.on_transfer_complete: Optional[Callable] = None
        self.on_message: Optional[Callable] = None
        self.on_file_list: Optional[Callable] = None
        self.latency = 0.0
    
    def start(self):
        self.running = True
        threading.Thread(target=self._handle_connection, daemon=True).start()
        threading.Thread(target=self._ping_loop, daemon=True).start()
    
    def stop(self):
        self.running = False
        try:
            self.sock.close()
        except:
            pass
    
    def _ping_loop(self):
        while self.running and self.authenticated:
            try:
                start = time.time()
                self._send_message(MessageType.PING, {})
                time.sleep(5)
            except:
                break
    
    def _send_message(self, msg_type: MessageType, data: Dict):
        message = {'type': msg_type.value, 'data': data}
        json_data = json.dumps(message).encode()
        
        if self.crypto.cipher and msg_type not in [MessageType.HANDSHAKE_INIT, MessageType.HANDSHAKE_RESPONSE]:
            json_data = self.crypto.encrypt(json_data)
        
        length = len(json_data)
        self.sock.sendall(length.to_bytes(4, 'big'))
        self.sock.sendall(json_data)
    
    def _receive_message(self) -> Optional[Dict]:
        try:
            length_bytes = self._recv_exact(4)
            if not length_bytes:
                return None
            length = int.from_bytes(length_bytes, 'big')
            data = self._recv_exact(length)
            if not data:
                return None
            if self.crypto.cipher:
                try:
                    data = self.crypto.decrypt(data)
                except:
                    pass
            return json.loads(data.decode())
        except:
            return None
    
    def _recv_exact(self, num_bytes: int) -> bytes:
        data = b''
        while len(data) < num_bytes:
            chunk = self.sock.recv(num_bytes - len(data))
            if not chunk:
                return b''
            data += chunk
        return data
    
    def _handle_connection(self):
        try:
            if self.is_initiator:
                self._initiate_handshake()
            while self.running:
                message = self._receive_message()
                if not message:
                    break
                self._process_message(message)
        except:
            pass
        finally:
            self.stop()
    
    def _initiate_handshake(self):
        symmetric_key = self.crypto.generate_symmetric_key()
        self.crypto.set_symmetric_key(symmetric_key)
        self._send_message(MessageType.HANDSHAKE_INIT, {
            'device_id': self.device_id,
            'public_key': base64.b64encode(self.crypto.get_public_key_bytes()).decode()
        })
    
    def _process_message(self, message: Dict):
        msg_type = MessageType(message['type'])
        data = message['data']
        
        handlers = {
            MessageType.HANDSHAKE_INIT: self._handle_handshake_init,
            MessageType.HANDSHAKE_RESPONSE: self._handle_handshake_response,
            MessageType.AUTH_REQUEST: self._handle_auth_request,
            MessageType.AUTH_RESPONSE: self._handle_auth_response,
            MessageType.FILE_LIST_REQUEST: self._handle_file_list_request,
            MessageType.FILE_LIST_RESPONSE: self._handle_file_list_response,
            MessageType.PING: self._handle_ping,
            MessageType.PONG: self._handle_pong,
        }
        
        handler = handlers.get(msg_type)
        if handler:
            handler(data)
    
    def _handle_handshake_init(self, data: Dict):
        self.peer_device_id = data['device_id']
        peer_public_key = base64.b64decode(data['public_key'])
        symmetric_key = self.crypto.generate_symmetric_key()
        self.crypto.set_symmetric_key(symmetric_key)
        encrypted_key = self.crypto.encrypt_symmetric_key(peer_public_key, symmetric_key)
        self._send_message(MessageType.HANDSHAKE_RESPONSE, {
            'device_id': self.device_id,
            'encrypted_key': base64.b64encode(encrypted_key).decode(),
            'public_key': base64.b64encode(self.crypto.get_public_key_bytes()).decode()
        })
        self._send_message(MessageType.AUTH_REQUEST, {'device_id': self.device_id})
    
    def _handle_handshake_response(self, data: Dict):
        self.peer_device_id = data['device_id']
        self._send_message(MessageType.AUTH_REQUEST, {'device_id': self.device_id})
    
    def _handle_auth_request(self, data: Dict):
        peer_id = data['device_id']
        if self.on_auth_request:
            authorized = self.on_auth_request(peer_id)
            self._send_message(MessageType.AUTH_RESPONSE, {'authorized': authorized})
            if authorized:
                self.authenticated = True
    
    def _handle_auth_response(self, data: Dict):
        if data['authorized']:
            self.authenticated = True
            if self.on_message:
                self.on_message(f"Connected")
    
    def _handle_file_list_request(self):
        if self.authenticated:
            self.file_manager.scan_shared_files()
            file_list = self.file_manager.get_file_list()
            self._send_message(MessageType.FILE_LIST_RESPONSE, {'files': file_list})
    
    def _handle_file_list_response(self, data: Dict):
        if self.on_file_list:
            self.on_file_list(data['files'])
    
    def _handle_ping(self, data: Dict):
        self._send_message(MessageType.PONG, {'timestamp': time.time()})
    
    def _handle_pong(self, data: Dict):
        self.latency = (time.time() - data.get('timestamp', time.time())) * 1000
    
    def request_file_list(self):
        if self.authenticated:
            self._send_message(MessageType.FILE_LIST_REQUEST, {})
    
    def send_file(self, file_metadata: FileMetadata):
        if not self.authenticated:
            return
        
        stats = TransferStats(
            filename=file_metadata.name,
            total_size=file_metadata.size,
            transferred=0,
            speed=0.0,
            eta=0.0,
            status='active',
            start_time=time.time()
        )
        self.transfer_stats[file_metadata.name] = stats
        
        with open(file_metadata.path, 'rb') as f:
            sent = 0
            start_time = time.time()
            
            while True:
                chunk = f.read(self.CHUNK_SIZE)
                if not chunk:
                    break
                
                encrypted_chunk = self.crypto.encrypt(chunk)
                sent += len(chunk)
                elapsed = time.time() - start_time
                speed = sent / elapsed if elapsed > 0 else 0
                eta = (file_metadata.size - sent) / speed if speed > 0 else 0
                
                stats.transferred = sent
                stats.speed = speed
                stats.eta = eta
                
                if self.on_transfer_progress:
                    self.on_transfer_progress(stats)
        
        stats.status = 'complete'
        if self.on_transfer_complete:
            self.on_transfer_complete(file_metadata.name)


class P2PServer:
    def __init__(self, device_id: str, crypto: CryptoManager, file_manager: FileManager, port: int = 5000):
        self.device_id = device_id
        self.crypto = crypto
        self.file_manager = file_manager
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.connections: List[P2PConnection] = []
        self.on_connection: Optional[Callable] = None
    
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        self.running = True
        threading.Thread(target=self._accept_connections, daemon=True).start()
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for conn in self.connections:
            conn.stop()
    
    def _accept_connections(self):
        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
                crypto = CryptoManager()
                connection = P2PConnection(client_sock, self.device_id, crypto, self.file_manager, False)
                self.connections.append(connection)
                if self.on_connection:
                    self.on_connection(connection)
                connection.start()
            except:
                break


class P2PClient:
    @staticmethod
    def connect(host: str, port: int, device_id: str, file_manager: FileManager) -> Optional[P2PConnection]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            sock.settimeout(None)
            crypto = CryptoManager()
            connection = P2PConnection(sock, device_id, crypto, file_manager, True)
            connection.start()
            return connection
        except:
            return None
