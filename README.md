# P2P Secure Transfer - Ultra-Minimalist Edition

End-to-end encrypted P2P file transfer with ultra-minimalist design and powerful features.

## Design Philosophy

**Ultra-Minimalist**: Pure black interface, no borders, maximum information density, zero configuration.

**Feature-Rich**: Peer management, real-time transfers, encryption status, network stats, file browser.

## Features

### Core
- **E2EE**: AES-256 + RSA-2048 encryption
- **Device ID System**: IP addresses never exposed
- **Zero Config**: Works immediately
- **Cross-Platform**: Windows, Linux, macOS

### File Management
- Scan shared folder
- Add files directly
- Browse local/remote files
- File metadata (size, hash, modified)
- Quick folder access

### Peer Management
- Add peers via IP:PORT
- Auto-generate Device IDs
- Connection status (online/offline)
- Network latency display
- Remove/manage peers

### Transfer Features
- Real-time progress tracking
- Transfer speed (KB/s, MB/s)
- ETA calculation
- Multiple simultaneous transfers
- Transfer history
- Upload all files at once

### Security
- Key fingerprint display
- Encryption algorithm shown
- Auto-authorization (configurable)
- Secure peer registry
- SHA-256 file verification

### Network
- Server status
- Active connections count
- Bandwidth monitoring
- Latency tracking
- Port configuration

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Terminal UI (Ultra-Minimal)
```bash
python p2p_transfer.py
```

**Keyboard Shortcuts:**
- `1` - Files tab
- `2` - Peers tab
- `3` - Transfers tab
- `r` - Refresh
- `c` - Connect to selected peer
- `u` - Upload all files
- `q` - Quit

### Graphical UI (Ultra-Minimal)
```bash
python p2p_transfer_gui.py
```

**Features:**
- Tabbed interface (Files, Peers, Transfers)
- Single-line status bar
- Pure black theme
- Instant updates

## Quick Start

### 1. Start Application
```bash
python p2p_transfer.py  # or p2p_transfer_gui.py
```

### 2. Add Files
- Go to Files tab
- Click "Scan" to scan `~/.p2p_transfer/shared/`
- Or add file path and click "Add"
- Or click "Open Folder" to add files manually

### 3. Add Peer
- Go to Peers tab
- Enter peer's IP:PORT (e.g., `192.168.1.100:5000`)
- Click "Add"
- Device ID is auto-generated

### 4. Connect
- Select peer in table
- Click "Connect" or press `c`
- Wait for "online" status

### 5. Transfer Files
- Go to Transfers tab
- Click "Upload All"
- Monitor progress in real-time

## Interface Design

### Terminal UI
```
┌─────────────────────────────────────────────────────────┐
│ Server:5000 | Peers:2 | Files:5 (12.3MB) | AES-256     │
├─────────────────────────────────────────────────────────┤
│ [Files] [Peers] [Transfers]                             │
│                                                          │
│ Name              Size      Hash                        │
│ document.pdf      2.3MB     A1B2C3D4                    │
│ image.jpg         1.1MB     E5F6G7H8                    │
│                                                          │
│ [Scan] [Add File] [Open Folder]                         │
└─────────────────────────────────────────────────────────┘
```

### GUI
- **Pure black background** (#000000)
- **Minimal gray accents** (#111111, #222222)
- **White text** (#ffffff)
- **No borders or gradients**
- **Monospace font**
- **Single-line status bar**

## Status Bar Information

**Device Bar (Top):**
```
Device ID: A1B2-C3D4-E5F6 | Key Fingerprint: 1A2B3C4D5E6F7G8H
```

**Status Bar (Second Line):**
```
Server:5000 | Peers:2 | Files:5 (12.3MB) | Encryption:AES-256
```

- **Device ID**: Your unique identifier (always visible)
- **Key**: Encryption key fingerprint (for verification)
- **Server**: Port number
- **Peers**: Active connections
- **Files**: Shared files count and total size
- **Encryption**: Algorithm in use

## File Structure

```
~/.p2p_transfer/
├── device_id.txt       # Your device ID
├── peers.json          # Peer registry (ID to IP mapping)
├── shared/             # Files to share
└── downloads/          # Received files
```

## Architecture

### Core Components
- `p2p_core.py` - Shared backend (crypto, networking, file management)
- `p2p_transfer.py` - Terminal UI (Textual)
- `p2p_transfer_gui.py` - Graphical UI (PyQt6)

### Key Classes
- `DeviceID` - Hardware-based ID generation
- `PeerRegistry` - Peer management with status tracking
- `CryptoManager` - E2EE with key fingerprints
- `FileManager` - File scanning and metadata
- `P2PConnection` - Individual peer connection with stats
- `P2PServer` - Accept incoming connections
- `P2PClient` - Initiate outgoing connections

## Security

### Encryption
- **Symmetric**: AES-256 (Fernet)
- **Asymmetric**: RSA-2048
- **Hashing**: SHA-256
- **Key Exchange**: RSA-OAEP

### Privacy
- Device IDs never displayed
- IP addresses never shown
- Peer registry encrypted storage
- Secure key fingerprints

### Verification
- File hash verification
- Key fingerprint display
- Connection status tracking
- Audit trail in logs

## Advanced Features

### Transfer Management
- Real-time progress bars
- Speed calculation (bytes/sec)
- ETA estimation
- Transfer status (active/complete/failed)
- Multiple simultaneous transfers

### Peer Status
- Online/offline detection
- Last seen timestamp
- Network latency (ping/pong)
- Connection quality

### File Operations
- Automatic folder scanning
- File metadata extraction
- Hash calculation
- Size formatting (KB/MB/GB)

## Performance

- **Chunk Size**: 128KB for optimal speed
- **Compression**: Optional gzip compression
- **Threading**: Concurrent transfers
- **Memory**: Efficient streaming
- **Network**: Automatic retry logic

## Troubleshooting

### Connection Failed
- Check firewall allows port 5000
- Verify peer's server is running
- Ensure correct IP address
- Check network connectivity

### Files Not Showing
- Click "Scan" to refresh
- Verify files in `~/.p2p_transfer/shared/`
- Check file permissions

### Slow Transfers
- Check network speed
- Reduce concurrent transfers
- Verify no bandwidth limits

### Peer Not Found
- Ensure peer is added first
- Check `~/.p2p_transfer/peers.json`
- Re-add peer if necessary

## Keyboard Shortcuts (TUI)

| Key | Action |
|-----|--------|
| `1` | Switch to Files tab |
| `2` | Switch to Peers tab |
| `3` | Switch to Transfers tab |
| `r` | Refresh all data |
| `c` | Connect to selected peer |
| `u` | Upload all files |
| `q` | Quit application |

## Configuration

All settings stored in `~/.p2p_transfer/`:

- **device_id.txt**: Your unique identifier
- **peers.json**: Known peers with status
- **shared/**: Files available for transfer
- **downloads/**: Received files location

## Development

### Extend Features
1. Edit `p2p_core.py` for backend changes
2. Update `p2p_transfer.py` for TUI
3. Update `p2p_transfer_gui.py` for GUI

### Add Message Types
1. Add to `MessageType` enum
2. Implement handler in `P2PConnection`
3. Update UI to trigger/display

### Customize UI
- TUI: Edit CSS in `P2PApp.CSS`
- GUI: Edit stylesheet in `init_ui()`

## License

Educational and personal use.

## Credits

Built with:
- Textual (TUI framework)
- PyQt6 (GUI framework)
- cryptography (Encryption)
- Python 3.8+
