#!/usr/bin/env python3
"""
P2P Secure Transfer - Ultra-Minimalist GUI
Feature-rich graphical interface
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import threading
import time

from p2p_core import *


def main():
    """Entry point for the application"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = P2PMainWindow()
    window.show()
    sys.exit(app.exec())


class UpdateSignals(QObject):
    update_status = pyqtSignal()
    update_files = pyqtSignal()
    update_peers = pyqtSignal()
    update_transfers = pyqtSignal()
    log_message = pyqtSignal(str)


class MinimalTable(QTableWidget):
    def __init__(self, headers):
        super().__init__()
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.context_menu_callback = None
    
    def show_context_menu(self, position):
        if self.context_menu_callback:
            self.context_menu_callback(position)


class P2PMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.signals = UpdateSignals()
        self.signals.update_status.connect(self.refresh_status)
        self.signals.update_files.connect(self.refresh_files)
        self.signals.update_peers.connect(self.refresh_peers)
        self.signals.update_transfers.connect(self.refresh_transfers)
        
        # Initialize P2P components
        self.config_dir = Path.home() / '.p2p_transfer'
        self.config_dir.mkdir(exist_ok=True)
        
        # Start server first to get actual port
        self.crypto = CryptoManager()
        self.shared_dir = self.config_dir / 'shared'
        self.file_manager = FileManager(self.shared_dir)
        
        # Try to start server on port 5000, if busy use 5001, 5002, etc.
        self.server_port = 5000
        temp_device_id = DeviceID.generate()
        self.server = P2PServer(temp_device_id, self.crypto, self.file_manager, self.server_port)
        
        # Set callback BEFORE starting server
        self.server.on_connection = self.handle_new_connection
        
        self.server.start()
        self.server_port = self.server.port  # Get actual port used
        
        # ALWAYS generate fresh Device ID with actual port (don't cache)
        from p2p_core import get_local_ip
        local_ip = get_local_ip()
        self.shareable_device_id = DeviceID.encode_with_ip(local_ip, self.server_port)
        self.device_id = self.shareable_device_id
        
        print(f"Generated Device ID: {self.device_id} for port {self.server_port}")
        
        # Update server with correct device ID
        self.server.device_id = self.device_id
        
        self.downloads_dir = self.config_dir / 'downloads'
        self.downloads_dir.mkdir(exist_ok=True)
        
        self.registry_file = self.config_dir / 'peers.json'
        self.peer_registry = PeerRegistry(self.registry_file)
        
        self.connections: List[P2PConnection] = []
        
        self.init_ui()
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all)
        self.timer.start(1000)
    
    def init_ui(self):
        self.setWindowTitle("P2P Secure Transfer")
        self.setFixedSize(900, 650)
        
        # Ultra-minimal black theme
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #000000;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 10px;
            }
            QTabWidget::pane {
                border: 1px solid #1a1a1a;
                background-color: #000000;
                padding: 5px;
            }
            QTabBar::tab {
                background-color: #0a0a0a;
                color: #888888;
                padding: 10px 20px;
                border: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #111111;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #0f0f0f;
                color: #cccccc;
            }
            QTableWidget {
                background-color: #000000;
                border: 1px solid #1a1a1a;
                gridline-color: #0a0a0a;
            }
            QTableWidget::item {
                padding: 6px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #1a1a1a;
            }
            QTableWidget::item:hover {
                background-color: #0f0f0f;
            }
            QHeaderView::section {
                background-color: #111111;
                color: #ffffff;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #0f0f0f;
                border: 1px solid #1a1a1a;
                padding: 8px;
                color: #ffffff;
                border-radius: 2px;
            }
            QLineEdit:focus {
                background-color: #151515;
                border: 1px solid #2a2a2a;
            }
            QPushButton {
                background-color: #0f0f0f;
                border: 1px solid #1a1a1a;
                padding: 8px 16px;
                color: #ffffff;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #1a1a1a;
                border: 1px solid #2a2a2a;
            }
            QPushButton:pressed {
                background-color: #1f1f1f;
            }
            QStatusBar {
                background-color: #111111;
                color: #ffffff;
                border-top: 1px solid #1a1a1a;
            }
            QLabel#device_label {
                background-color: #0a0a0a;
                color: #888888;
                padding: 8px;
                border-bottom: 1px solid #1a1a1a;
            }
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Device ID bar with copy button
        device_bar = QWidget()
        device_bar.setObjectName("device_bar")
        device_layout = QHBoxLayout(device_bar)
        device_layout.setContentsMargins(10, 5, 10, 5)
        
        self.device_label = QLabel()
        self.device_label.setObjectName("device_label")
        device_layout.addWidget(self.device_label)
        
        copy_id_btn = QPushButton("Copy ID")
        copy_id_btn.clicked.connect(self.copy_device_id)
        device_layout.addWidget(copy_id_btn)
        
        copy_key_btn = QPushButton("Copy Key")
        copy_key_btn.clicked.connect(self.copy_key)
        device_layout.addWidget(copy_key_btn)
        
        layout.addWidget(device_bar)
        
        # Tabs
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        
        # Files tab
        files_tab = QWidget()
        files_layout = QVBoxLayout(files_tab)
        files_layout.setContentsMargins(15, 15, 15, 15)
        files_layout.setSpacing(10)
        
        file_controls = QHBoxLayout()
        
        browse_btn = QPushButton("Add File (Browse)")
        browse_btn.clicked.connect(self.browse_file)
        file_controls.addWidget(browse_btn)
        
        scan_btn = QPushButton("Scan Folder")
        scan_btn.clicked.connect(self.scan_files)
        file_controls.addWidget(scan_btn)
        
        open_btn = QPushButton("Open Folder")
        open_btn.clicked.connect(self.open_shared_folder)
        file_controls.addWidget(open_btn)
        
        file_controls.addStretch()
        
        files_layout.addLayout(file_controls)
        
        self.files_table = MinimalTable(["Name", "Size", "Hash", "Modified"])
        self.files_table.context_menu_callback = self.show_files_context_menu
        files_layout.addWidget(self.files_table)
        
        tabs.addTab(files_tab, "Files")
        
        # Peers tab
        peers_tab = QWidget()
        peers_layout = QVBoxLayout(peers_tab)
        peers_layout.setContentsMargins(15, 15, 15, 15)
        peers_layout.setSpacing(10)
        
        # Info label
        info_label = QLabel("Your Device ID is shown at the top. Share it with peers to connect.")
        info_label.setStyleSheet("color: #666666; padding: 5px;")
        peers_layout.addWidget(info_label)
        
        # Add peer section
        peer_controls = QHBoxLayout()
        self.peer_input = QLineEdit()
        self.peer_input.setPlaceholderText("Paste Device ID here")
        self.peer_input.returnPressed.connect(self.add_peer)
        peer_controls.addWidget(self.peer_input)
        
        add_peer_btn = QPushButton("Add Peer")
        add_peer_btn.clicked.connect(self.add_peer)
        peer_controls.addWidget(add_peer_btn)
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect_peer)
        peer_controls.addWidget(connect_btn)
        
        disconnect_btn = QPushButton("Disconnect")
        disconnect_btn.clicked.connect(self.disconnect_peer)
        peer_controls.addWidget(disconnect_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_peer)
        peer_controls.addWidget(remove_btn)
        
        peers_layout.addLayout(peer_controls)
        
        self.peers_table = MinimalTable(["Device ID", "Status", "Latency", "Files"])
        self.peers_table.context_menu_callback = self.show_peers_context_menu
        peers_layout.addWidget(self.peers_table)
        
        tabs.addTab(peers_tab, "Peers")
        
        # Transfers tab
        transfers_tab = QWidget()
        transfers_layout = QVBoxLayout(transfers_tab)
        transfers_layout.setContentsMargins(15, 15, 15, 15)
        transfers_layout.setSpacing(10)
        
        transfer_controls = QHBoxLayout()
        
        upload_btn = QPushButton("Upload All")
        upload_btn.clicked.connect(self.upload_all)
        transfer_controls.addWidget(upload_btn)
        
        request_btn = QPushButton("Request Files")
        request_btn.clicked.connect(self.request_files)
        transfer_controls.addWidget(request_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_transfers)
        transfer_controls.addWidget(clear_btn)
        
        transfer_controls.addStretch()
        
        transfers_layout.addLayout(transfer_controls)
        
        self.transfers_table = MinimalTable(["File", "Progress", "Speed", "ETA", "Status"])
        self.transfers_table.context_menu_callback = self.show_transfers_context_menu
        transfers_layout.addWidget(self.transfers_table)
        
        tabs.addTab(transfers_tab, "Transfers")
        
        layout.addWidget(tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Initializing...")
    
    def start_server(self):
        self.server.on_connection = self.handle_new_connection
        self.server.start()
        self.file_manager.scan_shared_files()
        self.refresh_all()
    
    def update_all(self):
        self.signals.update_status.emit()
        self.signals.update_transfers.emit()
    
    def refresh_all(self):
        self.refresh_status()
        self.refresh_files()
        self.refresh_peers()
        self.refresh_transfers()
    
    def refresh_status(self):
        active_conns = len([c for c in self.connections if c.authenticated])
        files_count = len(self.file_manager.shared_files)
        total_size = sum(f.size for f in self.file_manager.shared_files) / (1024*1024)
        fingerprint = self.crypto.get_key_fingerprint()
        
        # Device ID bar - show port to differentiate instances
        device_info = f"Device ID: {self.device_id}  |  Port: {self.server_port}  |  Key: {fingerprint}"
        self.device_label.setText(device_info)
        
        # Status bar
        status = f"Server:{self.server_port} | Peers:{active_conns} | Files:{files_count} ({total_size:.1f}MB) | Encryption:AES-256"
        self.status_bar.showMessage(status)
    
    def refresh_files(self):
        self.files_table.setRowCount(0)
        for file in self.file_manager.shared_files:
            row = self.files_table.rowCount()
            self.files_table.insertRow(row)
            size_str = f"{file.size/(1024*1024):.2f}MB" if file.size > 1024*1024 else f"{file.size/1024:.1f}KB"
            from datetime import datetime
            modified = datetime.fromtimestamp(file.modified).strftime("%Y-%m-%d %H:%M")
            self.files_table.setItem(row, 0, QTableWidgetItem(file.name))
            self.files_table.setItem(row, 1, QTableWidgetItem(size_str))
            self.files_table.setItem(row, 2, QTableWidgetItem(file.hash[:12]))
            self.files_table.setItem(row, 3, QTableWidgetItem(modified))
    
    def refresh_peers(self):
        self.peers_table.setRowCount(0)
        for peer in self.peer_registry.get_all_peers():
            row = self.peers_table.rowCount()
            self.peers_table.insertRow(row)
            conn = next((c for c in self.connections if c.peer_device_id == peer.device_id), None)
            status = "online" if conn and conn.authenticated else "offline"
            latency = f"{conn.latency:.0f}ms" if conn and conn.authenticated else "-"
            files = "?" if not conn else "0"
            self.peers_table.setItem(row, 0, QTableWidgetItem(peer.device_id))
            self.peers_table.setItem(row, 1, QTableWidgetItem(status))
            self.peers_table.setItem(row, 2, QTableWidgetItem(latency))
            self.peers_table.setItem(row, 3, QTableWidgetItem(files))
    
    def refresh_transfers(self):
        self.transfers_table.setRowCount(0)
        for conn in self.connections:
            for filename, stats in conn.transfer_stats.items():
                row = self.transfers_table.rowCount()
                self.transfers_table.insertRow(row)
                progress = f"{(stats.transferred/stats.total_size*100):.1f}%"
                speed = f"{stats.speed/(1024*1024):.2f}MB/s" if stats.speed > 1024*1024 else f"{stats.speed/1024:.1f}KB/s"
                eta = f"{stats.eta:.0f}s" if stats.eta < 60 else f"{stats.eta/60:.1f}m"
                self.transfers_table.setItem(row, 0, QTableWidgetItem(filename))
                self.transfers_table.setItem(row, 1, QTableWidgetItem(progress))
                self.transfers_table.setItem(row, 2, QTableWidgetItem(speed))
                self.transfers_table.setItem(row, 3, QTableWidgetItem(eta))
                self.transfers_table.setItem(row, 4, QTableWidgetItem(stats.status))
    
    def handle_new_connection(self, connection: P2PConnection):
        connection.on_auth_request = lambda peer_id: True
        connection.on_message = lambda msg: None
        connection.on_transfer_progress = lambda stats: self.signals.update_transfers.emit()
        self.connections.append(connection)
        self.signals.update_peers.emit()
    
    def scan_files(self):
        self.file_manager.scan_shared_files()
        self.refresh_files()
        self.refresh_status()
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Add", str(Path.home()))
        if file_path:
            path = Path(file_path)
            if path.exists() and path.is_file():
                if self.file_manager.add_file_to_shared(path):
                    self.refresh_files()
                    self.refresh_status()
                    self.status_bar.showMessage(f"Added: {path.name}", 2000)
                else:
                    self.status_bar.showMessage(f"ERROR: Failed to add file", 3000)
    
    def add_file(self):
        # This method is no longer needed but kept for compatibility
        pass
    
    def open_shared_folder(self):
        import subprocess
        if sys.platform == 'darwin':
            subprocess.run(['open', str(self.shared_dir)])
        elif sys.platform == 'win32':
            subprocess.run(['explorer', str(self.shared_dir)])
        else:
            subprocess.run(['xdg-open', str(self.shared_dir)])
    
    def add_peer(self):
        """Add peer by Device ID (which contains IP info) or IP:PORT"""
        value = self.peer_input.text().strip()
        
        if not value:
            return
        
        print(f"DEBUG: Trying to add peer: {value}")
        
        # Try to decode as Device ID first
        ip_port = DeviceID.decode_to_ip(value)
        print(f"DEBUG: Decoded IP:PORT = {ip_port}")
        
        if ip_port:
            ip, port = ip_port
            print(f"DEBUG: Adding peer with IP={ip}, PORT={port}")
            self.peer_registry.add_peer(value, ip)
            self.refresh_peers()
            self.peer_input.clear()
            QMessageBox.information(self, "Success", f"Peer added!\nDevice ID: {value}\nIP: {ip}:{port}")
            return
        
        # Check if it's IP:PORT format (fallback)
        if ':' in value and '.' in value:
            try:
                ip, port = value.split(':')
                device_id = DeviceID.encode_with_ip(ip, int(port))
                print(f"DEBUG: Created Device ID from IP: {device_id}")
                self.peer_registry.add_peer(device_id, ip)
                self.refresh_peers()
                self.peer_input.clear()
                QMessageBox.information(self, "Success", f"Peer added!\nDevice ID: {device_id}")
            except Exception as e:
                print(f"DEBUG: Error with IP:PORT - {e}")
                QMessageBox.warning(self, "Error", f"Invalid IP:PORT format\n{e}")
        else:
            print(f"DEBUG: Invalid format")
            QMessageBox.warning(self, "Error", "Invalid Device ID format\nTry generating a new ID or use IP:PORT")
    
    

    
    
    def connect_peer(self):
        row = self.peers_table.currentRow()
        if row >= 0:
            peers = self.peer_registry.get_all_peers()
            if row < len(peers):
                peer = peers[row]
                
                # Decode Device ID to get actual IP and PORT
                ip_port = DeviceID.decode_to_ip(peer.device_id)
                if ip_port:
                    ip, port = ip_port
                    print(f"Connecting to {peer.device_id} at {ip}:{port}")
                    connection = P2PClient.connect(ip, port, self.device_id, self.file_manager)
                    if connection:
                        connection.on_auth_request = lambda peer_id: True
                        connection.on_message = lambda msg: None
                        connection.on_transfer_progress = lambda stats: self.signals.update_transfers.emit()
                        self.connections.append(connection)
                        
                        # Wait a bit for authentication
                        QTimer.singleShot(500, lambda: self.check_connection_status(peer.device_id))
                        
                        print(f"Connected to {peer.device_id}")
                    else:
                        print(f"Failed to connect to {peer.device_id}")
                else:
                    print(f"Failed to decode Device ID: {peer.device_id}")
    
    def check_connection_status(self, device_id):
        """Check if connection is authenticated and update status"""
        for conn in self.connections:
            if conn.peer_device_id == device_id and conn.authenticated:
                self.peer_registry.update_status(device_id, "online")
                self.refresh_peers()
                print(f"Authentication confirmed for {device_id}")
                return
        # Not authenticated yet, check again
        QTimer.singleShot(500, lambda: self.check_connection_status(device_id))
    
    def disconnect_peer(self):
        row = self.peers_table.currentRow()
        if row >= 0:
            peers = self.peer_registry.get_all_peers()
            if row < len(peers):
                peer = peers[row]
                for conn in self.connections:
                    if conn.peer_device_id == peer.device_id:
                        conn.stop()
                        self.connections.remove(conn)
                        break
                self.peer_registry.update_status(peer.device_id, "offline")
                self.refresh_peers()
    
    def copy_device_id(self):
        import pyperclip
        try:
            pyperclip.copy(self.device_id)
        except:
            pass
    
    def copy_key(self):
        import pyperclip
        try:
            pyperclip.copy(self.crypto.get_key_fingerprint())
        except:
            pass
    
    def show_files_context_menu(self, position):
        """Show context menu for files table"""
        row = self.files_table.currentRow()
        if row < 0 or row >= len(self.file_manager.shared_files):
            return
        
        file = self.file_manager.shared_files[row]
        
        menu = QMenu(self.files_table)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #2a2a2a;
            }
            QMenu::item:selected {
                background-color: #2a2a2a;
            }
        """)
        
        properties_action = menu.addAction("Properties")
        copy_name_action = menu.addAction("Copy Name")
        copy_hash_action = menu.addAction("Copy Hash")
        menu.addSeparator()
        open_location_action = menu.addAction("Open File Location")
        menu.addSeparator()
        remove_action = menu.addAction("Remove from List")
        delete_action = menu.addAction("Delete File")
        
        action = menu.exec(self.files_table.viewport().mapToGlobal(position))
        
        if action == properties_action:
            self.show_file_properties(file)
        elif action == copy_name_action:
            import pyperclip
            try:
                pyperclip.copy(file.name)
                self.status_bar.showMessage(f"Copied: {file.name}", 2000)
            except:
                pass
        elif action == copy_hash_action:
            import pyperclip
            try:
                pyperclip.copy(file.hash)
                self.status_bar.showMessage(f"Copied hash", 2000)
            except:
                pass
        elif action == open_location_action:
            import subprocess
            import sys
            file_path = Path(file.path)
            folder = file_path.parent
            try:
                if sys.platform == 'darwin':
                    subprocess.run(['open', str(folder)])
                elif sys.platform == 'win32':
                    subprocess.run(['explorer', str(folder)])
                else:
                    subprocess.run(['xdg-open', str(folder)])
            except:
                pass
        elif action == remove_action:
            self.file_manager.shared_files.pop(row)
            self.refresh_files()
            self.refresh_status()
        elif action == delete_action:
            reply = QMessageBox.question(
                self, 'Delete File',
                f'Are you sure you want to delete {file.name}?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    Path(file.path).unlink()
                    self.file_manager.scan_shared_files()
                    self.refresh_files()
                    self.refresh_status()
                    self.status_bar.showMessage(f"Deleted: {file.name}", 2000)
                except Exception as e:
                    self.status_bar.showMessage(f"Error: {str(e)}", 3000)
    
    def show_file_properties(self, file):
        """Show file properties dialog"""
        from datetime import datetime
        
        dialog = QDialog(self)
        dialog.setWindowTitle("File Properties")
        dialog.setFixedSize(500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                padding: 5px;
            }
            QTextEdit {
                background-color: #0f0f0f;
                border: 1px solid #2a2a2a;
                color: #ffffff;
                padding: 10px;
            }
            QPushButton {
                background-color: #0f0f0f;
                border: 1px solid #2a2a2a;
                padding: 8px 16px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #2a2a2a;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        info = QTextEdit()
        info.setReadOnly(True)
        
        size_mb = file.size / (1024 * 1024)
        size_kb = file.size / 1024
        modified = datetime.fromtimestamp(file.modified).strftime("%Y-%m-%d %H:%M:%S")
        
        properties_text = f"""
FILE PROPERTIES

Name: {file.name}
Path: {file.path}

Size: {file.size:,} bytes ({size_mb:.2f} MB / {size_kb:.2f} KB)
Modified: {modified}

Hash (SHA-256):
{file.hash}

Type: {Path(file.name).suffix or 'No extension'}
"""
        
        info.setPlainText(properties_text)
        layout.addWidget(info)
        
        btn_layout = QHBoxLayout()
        
        copy_hash_btn = QPushButton("Copy Hash")
        copy_hash_btn.clicked.connect(lambda: self.copy_to_clipboard(file.hash))
        btn_layout.addWidget(copy_hash_btn)
        
        copy_path_btn = QPushButton("Copy Path")
        copy_path_btn.clicked.connect(lambda: self.copy_to_clipboard(file.path))
        btn_layout.addWidget(copy_path_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def copy_to_clipboard(self, text):
        import pyperclip
        try:
            pyperclip.copy(text)
            self.status_bar.showMessage("Copied to clipboard", 2000)
        except:
            pass
    
    def show_peers_context_menu(self, position):
        """Show context menu for peers table"""
        row = self.peers_table.currentRow()
        if row < 0:
            return
        
        peers = self.peer_registry.get_all_peers()
        if row >= len(peers):
            return
        
        peer = peers[row]
        
        menu = QMenu(self.peers_table)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #2a2a2a;
            }
            QMenu::item:selected {
                background-color: #2a2a2a;
            }
        """)
        
        connect_action = menu.addAction("Connect")
        disconnect_action = menu.addAction("Disconnect")
        menu.addSeparator()
        copy_id_action = menu.addAction("Copy Device ID")
        menu.addSeparator()
        remove_action = menu.addAction("Remove Peer")
        
        action = menu.exec(self.peers_table.viewport().mapToGlobal(position))
        
        if action == connect_action:
            self.connect_peer()
        elif action == disconnect_action:
            self.disconnect_peer()
        elif action == copy_id_action:
            import pyperclip
            try:
                pyperclip.copy(peer.device_id)
                self.status_bar.showMessage(f"Copied Device ID", 2000)
            except:
                pass
        elif action == remove_action:
            self.remove_peer()
    
    def show_transfers_context_menu(self, position):
        """Show context menu for transfers table"""
        row = self.transfers_table.currentRow()
        if row < 0:
            return
        
        menu = QMenu(self.transfers_table)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #2a2a2a;
            }
            QMenu::item:selected {
                background-color: #2a2a2a;
            }
        """)
        
        pause_action = menu.addAction("Pause")
        resume_action = menu.addAction("Resume")
        cancel_action = menu.addAction("Cancel")
        menu.addSeparator()
        clear_action = menu.addAction("Clear Completed")
        
        action = menu.exec(self.transfers_table.viewport().mapToGlobal(position))
        
        if action == clear_action:
            self.clear_transfers()
    
    def remove_peer(self):
        row = self.peers_table.currentRow()
        if row >= 0:
            peers = self.peer_registry.get_all_peers()
            if row < len(peers):
                peer = peers[row]
                self.peer_registry.remove_peer(peer.device_id)
                self.refresh_peers()
    
    def upload_all(self):
        print(f"Upload All clicked! Connections: {len(self.connections)}")
        for conn in self.connections:
            print(f"Connection authenticated: {conn.authenticated}")
            if conn.authenticated:
                print(f"Sending {len(self.file_manager.shared_files)} files")
                for file in self.file_manager.shared_files:
                    print(f"Sending file: {file.name}")
                    threading.Thread(target=conn.send_file, args=(file,), daemon=True).start()
            else:
                print("Connection not authenticated yet!")
    
    def request_files(self):
        for conn in self.connections:
            if conn.authenticated:
                conn.request_file_list()
    
    def clear_transfers(self):
        for conn in self.connections:
            conn.transfer_stats.clear()
        self.refresh_transfers()
    
    def closeEvent(self, event):
        self.server.stop()
        for conn in self.connections:
            conn.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = P2PMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
